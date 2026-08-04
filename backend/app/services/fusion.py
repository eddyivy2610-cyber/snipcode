"""
services/fusion.py
==================
IR v5.0 Master Sensor Fusion Engine & Universal UI Compiler.

Transforms raw YOLO detections, EasyOCR text strings, and ScreenParser semantics
into IR v5.0 AST:
  - Label-Input Disaggregation (Label + Input linked via 'for' / 'id' pointers)
  - Strict Form & Card Container Tree Encapsulation
  - Weighted Mathematical Sensor Confidence Fusion (YOLO + OCR + ScreenParser)
  - Explicit Provenance Object mapping
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List

from app.services.detector import detect
from app.services.ocr import perform_full_ocr, perform_ocr
from app.services.screenparser import parse_screen

logger = logging.getLogger(__name__)


def compute_iou(boxA: List[float], boxB: List[float]) -> float:
    """Compute Intersection Over Union (IoU) between two [xmin, ymin, xmax, ymax] boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    if interArea == 0.0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(boxAArea + boxBArea - interArea)


def compute_fused_confidence(
    yolo_conf: float,
    ocr_conf: float,
    sp_conf: float
) -> float:
    """
    Weighted Mathematical Sensor Confidence Fusion:
      YOLO (0.40) + EasyOCR (0.40) + ScreenParser (0.20)
    """
    fused = (0.40 * yolo_conf) + (0.40 * ocr_conf) + (0.20 * sp_conf)
    return round(float(fused), 2)


def slugify(text: str) -> str:
    """Convert string to clean identifier token (e.g. 'Sign Up' -> 'signup')."""
    s = re.sub(r'[^a-zA-Z0-9]', '_', text.lower()).strip('_')
    return s if s else "field"


def fuse_sensors(image_path: str) -> List[Dict[str, Any]]:
    """
    IR v5.0 Sensor Fusion Pipeline.

    Returns hierarchical IR v5.0 component nodes:
      - Form container wrapping children
      - Label + Input disaggregated pairs linked via 'for' pointers
      - Weighted fused confidence scores
      - Provenance tracking objects
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    logger.info(f"[IR v5.0 Fusion] Executing Sensor Fusion on: {image_path}")

    # 1. Sensors
    yolo_dets = detect(image_path)
    ocr_blocks = perform_full_ocr(image_path)
    sp_data = parse_screen(image_path, output_json_path=None)
    sp_components = sp_data.get("components", [])

    matched_ocr_indices = set()
    raw_nodes: List[Dict[str, Any]] = []

    # Process YOLO detections
    for idx, det in enumerate(yolo_dets):
        bbox = [float(v) for v in det["bbox"]]
        y_class = det["class"]
        y_conf = float(det["confidence"])

        # Match EasyOCR blocks inside bounding box
        intersecting_ocr = []
        for o_idx, block in enumerate(ocr_blocks):
            bx1, by1, bx2, by2 = block["bbox"]
            cx = (bx1 + bx2) / 2
            cy = (by1 + by2) / 2
            if bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]:
                intersecting_ocr.append(block)
                matched_ocr_indices.add(o_idx)

        if intersecting_ocr:
            intersecting_ocr.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
            text_val = " ".join([b["text"] for b in intersecting_ocr]).strip()
            o_conf = max(b["confidence"] for b in intersecting_ocr)
        else:
            ocr_res = perform_ocr(image_path, bbox)
            text_val = ocr_res.get("text", "").strip()
            o_conf = ocr_res.get("confidence", 0.0)

        # Match ScreenParser semantic hints
        sp_match = None
        best_iou = 0.0
        for sp in sp_components:
            iou = compute_iou(bbox, sp.get("bbox", [0, 0, 0, 0]))
            if iou > best_iou:
                best_iou = iou
                sp_match = sp

        sp_conf = float(sp_match.get("confidence", 0.5)) if sp_match else 0.5
        fused_conf = compute_fused_confidence(y_conf, o_conf, sp_conf)

        raw_nodes.append({
            "yolo_type": y_class,
            "text": text_val,
            "bbox": bbox,
            "y_conf": y_conf,
            "o_conf": o_conf,
            "sp_conf": sp_conf,
            "fused_conf": fused_conf,
            "sp_match": sp_match,
        })

    # Include unmatched OCR blocks
    for o_idx, block in enumerate(ocr_blocks):
        if o_idx in matched_ocr_indices:
            continue
        text_val = block["text"].strip()
        if not text_val:
            continue

        raw_nodes.append({
            "yolo_type": "Text",
            "text": text_val,
            "bbox": [float(v) for v in block["bbox"]],
            "y_conf": 0.5,
            "o_conf": float(block["confidence"]),
            "sp_conf": 0.5,
            "fused_conf": compute_fused_confidence(0.5, float(block["confidence"]), 0.5),
            "sp_match": None,
        })

    # Sort nodes by vertical reading order (top to bottom)
    raw_nodes.sort(key=lambda n: (n["bbox"][1], n["bbox"][0]))

    # Construct IR v5.0 Schema
    form_children: List[Dict[str, Any]] = []

    for idx, node in enumerate(raw_nodes):
        y_type = node["yolo_type"]
        text_val = node["text"]
        lower_t = text_val.lower().strip()
        bbox = node["bbox"]
        fused_conf = node["fused_conf"]

        # Provenance mapping
        provenance = {
            "layout": "YOLO",
            "text": "EasyOCR" if text_val else "YOLO-Crop",
            "semantics": "ScreenParser" if node["sp_match"] else "FusionHeuristics",
        }

        # IR v5.0 Disaggregation Logic:
        # Check if node is an Input field or Button or Label
        if y_type == "Input" or "password" in lower_t or "email" in lower_t or "username" in lower_t:
            slug = slugify(text_val) if text_val else f"field_{idx+1}"
            label_id = f"label_{slug}"
            input_id = f"input_{slug}"

            input_type = "text"
            if "password" in lower_t:
                input_type = "password"
            elif "email" in lower_t:
                input_type = "email"
            elif "search" in lower_t:
                input_type = "search"

            # 1. Label Node
            label_node = {
                "id": label_id,
                "type": "Label",
                "content": {
                    "text": text_val or slug.capitalize(),
                },
                "for": input_id,
                "bbox": [bbox[0], max(0, bbox[1] - 25), bbox[2], bbox[1]],
                "confidence": fused_conf,
                "provenance": provenance,
            }

            # 2. Input Node
            input_node = {
                "id": input_id,
                "type": "Input",
                "input_type": input_type,
                "placeholder": f"Enter {text_val.lower() if text_val else slug}",
                "bbox": bbox,
                "confidence": fused_conf,
                "provenance": provenance,
            }

            if input_type == "password":
                input_node["trailing_icon"] = "eye"

            form_children.append(label_node)
            form_children.append(input_node)

        elif y_type in ["Button", "Link"]:
            slug = slugify(text_val) if text_val else f"action_{idx+1}"
            btn_id = f"btn_{slug}"

            role = "submit" if any(w in lower_t for w in ["submit", "sign up", "sign in", "login", "register", "continue"]) else "action"
            variant = "primary" if role == "submit" else "outlined"

            btn_node = {
                "id": btn_id,
                "type": "Button",
                "role": role,
                "variant": variant,
                "content": {
                    "text": text_val or "Action",
                },
                "bbox": bbox,
                "confidence": fused_conf,
                "provenance": provenance,
            }
            form_children.append(btn_node)

        else:
            # General Text / Title Label Node
            slug = slugify(text_val) if text_val else f"text_{idx+1}"
            text_node = {
                "id": f"text_{slug}",
                "type": "Label" if any(w in lower_t for w in ["form", "title", "header"]) else "Text",
                "content": {
                    "text": text_val,
                },
                "bbox": bbox,
                "confidence": fused_conf,
                "provenance": provenance,
            }
            form_children.append(text_node)

    # Encapsulate into Form / Screen Root Container
    ir_v5_tree = [
        {
            "id": "form_main",
            "type": "Form",
            "children": form_children,
            "provenance": {
                "layout": "YOLO",
                "text": "EasyOCR",
                "semantics": "ScreenParser",
            },
        }
    ]

    return ir_v5_tree


if __name__ == "__main__":
    import json
    import sys
    logging.basicConfig(level=logging.INFO)

    test_img = "uploads/Screenshot (19).png"
    if len(sys.argv) > 1:
        test_img = sys.argv[1]

    if not os.path.exists(test_img):
        test_img = "backend/uploads/Screenshot (19).png"

    if os.path.exists(test_img):
        print(f"--- Testing IR v5.0 Sensor Fusion (`fusion.py`) ---")
        print(f"Target Image: {test_img}")
        res = fuse_sensors(test_img)

        out_path = "ir_v5_output.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)

        print(f"\nSUCCESS! IR v5.0 AST saved to {out_path}")
        print("\nIR v5.0 AST Output Preview:")
        print(json.dumps(res, indent=2))
