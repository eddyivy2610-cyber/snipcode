import logging
import os
from typing import Dict

import cv2
import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)

# Lazy-loaded EasyOCR reader
_reader = None


def get_ocr_reader():
    """
    Initialize EasyOCR only once.
    Uses GPU automatically if available.
    Caches model weights in the local workspace directory to avoid repeated downloads.
    """
    global _reader

    if _reader is not None:
        return _reader

    try:
        import easyocr
        model_dir = os.path.join(os.path.dirname(__file__), "models", "ocr")
        os.makedirs(model_dir, exist_ok=True)
        use_gpu = torch.cuda.is_available()
        _reader = easyocr.Reader(['en'], gpu=use_gpu, model_storage_directory=model_dir)
        logger.info(f"EasyOCR reader initialized successfully (GPU={use_gpu}, cache={model_dir}).")
    except Exception as e:
        logger.exception(f"Failed to initialize EasyOCR: {e}")
        _reader = False

    return _reader


# ---------------------------------------------------------------------------
# Improvement #2: Image Pre-Processing for OCR
# ---------------------------------------------------------------------------

def _preprocess_for_ocr(crop_bgr: np.ndarray) -> np.ndarray:
    """
    Enhance a cropped region for better EasyOCR accuracy.

    Steps applied:
      1. Upscale to at least 64px tall so small characters are readable
      2. Convert to grayscale
      3. CLAHE adaptive histogram equalisation for contrast normalisation
      4. Light Gaussian blur to reduce JPEG / compression artefacts
      5. Adaptive thresholding to produce crisp black-on-white text

    Returns an enhanced RGB numpy array ready for EasyOCR.
    """
    h, w = crop_bgr.shape[:2]

    # 1. Upscale tiny crops to make text legible
    min_height = 64
    if h < min_height:
        scale = min_height / max(h, 1)
        new_w = max(1, int(w * scale))
        new_h = min_height
        crop_bgr = cv2.resize(crop_bgr, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    # 2. Greyscale conversion
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)

    # 3. CLAHE adaptive histogram equalisation
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Light Gaussian blur to remove sensor/compression noise
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # 5. Adaptive threshold → sharp binary text
    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2
    )

    # Convert back to RGB for EasyOCR
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)


def perform_ocr(
    image_path: str,
    bbox: list,
    confidence_threshold: float = 0.30,
    padding: int = 6              # Improvement #2: increased padding 4px → 6px
) -> Dict:
    """
    Runs OCR on a cropped region with image pre-processing for improved accuracy.

    Parameters
    ----------
    image_path : str   Path to image.
    bbox       : list  [xmin, ymin, xmax, ymax]
    confidence_threshold : float  Minimum OCR confidence.
    padding    : int   Extra pixel border around the bbox before cropping.

    Returns
    -------
    dict  {"text": str, "confidence": float}
    """
    reader = get_ocr_reader()

    if not reader:
        return {"text": "", "confidence": 0.0}

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            xmin, ymin, xmax, ymax = bbox

            # Apply padded crop
            xmin = max(0, int(xmin) - padding)
            ymin = max(0, int(ymin) - padding)
            xmax = min(width, int(xmax) + padding)
            ymax = min(height, int(ymax) + padding)

            if xmax <= xmin or ymax <= ymin:
                return {"text": "", "confidence": 0.0}

            crop_pil = img.crop((xmin, ymin, xmax, ymax)).convert("RGB")

        # Convert PIL → BGR for OpenCV pre-processing
        crop_bgr = cv2.cvtColor(np.array(crop_pil), cv2.COLOR_RGB2BGR)
        crop_enhanced = _preprocess_for_ocr(crop_bgr)

        results = reader.readtext(crop_enhanced)

        if not results:
            return {"text": "", "confidence": 0.0}

        valid = [r for r in results if r[2] >= confidence_threshold]

        if not valid:
            return {"text": "", "confidence": 0.0}

        text = " ".join([r[1] for r in valid]).strip()
        confidence = max(r[2] for r in valid)

        return {"text": text, "confidence": float(confidence)}

    except Exception as e:
        logger.exception(f"OCR failed: {e}")
        return {"text": "", "confidence": 0.0}


def perform_full_ocr(image_path: str) -> list:
    """
    Run OCR on the entire image and return a list of text blocks.
    Each block: {"text": str, "bbox": [xmin, ymin, xmax, ymax], "confidence": float}
    Applies CLAHE + adaptive threshold pre-processing for improved accuracy.
    """
    reader = get_ocr_reader()
    if not reader:
        return []

    try:
        with Image.open(image_path) as img:
            img_rgb = np.array(img.convert("RGB"))

        # Pre-process the full image for better full-page OCR
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        img_for_ocr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

        results = reader.readtext(img_for_ocr)
        blocks = []
        for res in results:
            # res is ([[x0, y0], [x1, y1], [x2, y2], [x3, y3]], text, confidence)
            coords = res[0]
            text = res[1].strip()
            conf = res[2]

            if not text or conf < 0.25:
                continue

            # Convert 4 corner-points → xmin, ymin, xmax, ymax
            xs = [p[0] for p in coords]
            ys = [p[1] for p in coords]
            xmin, ymin, xmax, ymax = min(xs), min(ys), max(xs), max(ys)

            blocks.append({
                "text": text,
                "bbox": [float(xmin), float(ymin), float(xmax), float(ymax)],
                "confidence": float(conf)
            })
        return blocks
    except Exception as e:
        logger.exception(f"Full OCR failed: {e}")
        return []
