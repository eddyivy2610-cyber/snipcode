"""
services/screenparser.py
========================
Phase 1 — Standalone ScreenParser Service.

Responsibility:
  Input:  image.png
  Output: screenparser.json (and returned dict/list)

Supports HF layout models & visual fallback parsing.
Caches model weights in backend/app/models/screenparser/
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional
from PIL import Image

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

logger = logging.getLogger(__name__)

HF_MODEL_ID = "microsoft/table-transformer-detection"
LOCAL_MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "screenparser"))

_model = None
_image_processor = None


def get_screenparser_model():
    """
    Lazy-loads HuggingFace layout parser model.
    Caches model weights in backend/app/models/screenparser/
    """
    global _model, _image_processor

    if _model is not None:
        return _model, _image_processor

    # On low-RAM free tier containers (512MB RAM), default to fast lightweight visual engine
    if os.getenv("DISABLE_HF_SCREENPARSER", "1") == "1":
        logger.info("[ScreenParser] Using lightweight visual ScreenParser engine (DISABLE_HF_SCREENPARSER=1).")
        return None, None

    try:
        from transformers import AutoImageProcessor, AutoModelForObjectDetection
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        _image_processor = AutoImageProcessor.from_pretrained(HF_MODEL_ID, cache_dir=LOCAL_MODEL_DIR)
        _model = AutoModelForObjectDetection.from_pretrained(
            HF_MODEL_ID,
            cache_dir=LOCAL_MODEL_DIR
        ).to(device)

        logger.info(f"[ScreenParser] Loaded HuggingFace ScreenParser model successfully on device={device}")
        return _model, _image_processor
    except Exception as e:
        logger.warning(f"[ScreenParser] Using visual semantic ScreenParser engine ({e}).")
        return None, None


def parse_screen(
    image_path: str,
    output_json_path: Optional[str] = "screenparser.json"
) -> Dict[str, Any]:
    """
    Parse a screenshot image into ScreenParser JSON output:
      - Semantic Types (Primary Button, Search Input, Card Container, Form)
      - Component Roles (submit, navigate, search, input_field, header)
      - Visual Variants (primary, secondary, outlined, ghost)
      - Bounding Boxes [xmin, ymin, xmax, ymax]

    Parameters
    ----------
    image_path : str
        Path to input screenshot (e.g. image.png).
    output_json_path : str, optional
        Path where screenparser.json will be saved. Defaults to 'screenparser.json'.

    Returns
    -------
    dict
        Parsed ScreenParser JSON output structure.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image path not found: {image_path}")

    with Image.open(image_path) as img:
        img_rgb = img.convert("RGB")
        width, height = img_rgb.size

    logger.info(f"[ScreenParser] Parsing screen image: {image_path} ({width}x{height})")

    model, image_processor = get_screenparser_model()

    components: List[Dict[str, Any]] = []

    if model and image_processor:
        try:
            import torch
            device = next(model.parameters()).device
            inputs = image_processor(images=img_rgb, return_tensors="pt").to(device)

            with torch.no_grad():
                outputs = model(**inputs)
                
            target_sizes = torch.tensor([[height, width]]).to(device)
            results = image_processor.post_process_object_detection(outputs, threshold=0.3, target_sizes=target_sizes)[0]
            
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                box_coords = [round(i, 1) for i in box.tolist()]
                label_name = model.config.id2label[label.item()]
                components.append({
                    "id": f"sp_hf_{len(components)+1}",
                    "type": label_name,
                    "role": "container" if "table" in label_name.lower() or "header" in label_name.lower() else "action",
                    "variant": "outlined",
                    "content": {"text": ""},
                    "bbox": box_coords,
                    "confidence": round(score.item(), 2),
                    "source": "HuggingFace-ScreenParser",
                })
        except Exception as err:
            logger.exception(f"[ScreenParser] Neural inference exception: {err}")

    # Fallback / Enrich with EasyOCR + YOLO UI parser
    if not components:
        components = _fallback_parse(image_path, width, height)

    parsed_output: Dict[str, Any] = {
        "metadata": {
            "source_image": os.path.basename(image_path),
            "width": width,
            "height": height,
            "engine": "ScreenParser-v1.0",
            "total_elements": len(components),
        },
        "components": components,
    }

    # Save screenparser.json if output path provided
    if output_json_path:
        out_dir = os.path.dirname(output_json_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_output, f, indent=2)
        logger.info(f"[ScreenParser] Saved parsed JSON output to: {output_json_path}")

    return parsed_output


def _fallback_parse(image_path: str, width: int, height: int) -> List[Dict[str, Any]]:
    """Enriched ScreenParser component extraction."""
    from app.services.detector import detect
    from app.services.ocr import perform_full_ocr

    raw_dets = detect(image_path)
    ocr_blocks = perform_full_ocr(image_path)

    components = []
    for idx, det in enumerate(raw_dets):
        bbox = [float(v) for v in det["bbox"]]
        cls_name = det["class"]

        matched_text = []
        for block in ocr_blocks:
            bx1, by1, bx2, by2 = block["bbox"]
            cx = (bx1 + bx2) / 2
            cy = (by1 + by2) / 2
            if bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]:
                matched_text.append(block["text"])

        text_content = " ".join(matched_text).strip()
        lower_text = text_content.lower()

        sem_type = cls_name
        role = "generic"
        variant = "standard"

        if cls_name in ["Button", "Link"]:
            if any(w in lower_text for w in ["submit", "sign up", "sign in", "login", "register", "continue", "create"]):
                sem_type = "Primary Button"
                role = "submit"
                variant = "primary"
            else:
                sem_type = "Action Button"
                role = "action"
                variant = "outlined"

        elif cls_name in ["Input", "Text"]:
            if any(w in lower_text for w in ["email", "password", "username"]):
                sem_type = "Form Input"
                role = "input_field"
                variant = "outlined"

        components.append({
            "id": f"sp_comp_{idx + 1}",
            "type": sem_type,
            "role": role,
            "variant": variant,
            "content": {"text": text_content},
            "bbox": bbox,
            "confidence": round(float(det["confidence"]), 2),
            "source": "ScreenParser",
        })
    return components


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    test_img = "uploads/Screenshot (19).png"
    if len(sys.argv) > 1:
        test_img = sys.argv[1]

    if not os.path.exists(test_img):
        test_img = "backend/uploads/Screenshot (19).png"

    if os.path.exists(test_img):
        print(f"--- Running ScreenParser Inference ---")
        print(f"Target Image: {test_img}")
        res = parse_screen(test_img, output_json_path="screenparser.json")
        print(f"\nSUCCESS! Output written to screenparser.json ({len(res['components'])} elements parsed)")
