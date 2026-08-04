"""
services/detector.py
====================
Pure YOLO detection — no OCR.

Returns bare detections so the merger service can pair them with OCR
results as a separate, testable step.
"""

from ultralytics import YOLO

import os

_model: YOLO | None = None
_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "best.pt"))


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(_MODEL_PATH)
    return _model


def detect(image_path: str) -> list[dict]:
    """
    Run YOLO on *image_path* and return raw detections.

    Returns
    -------
    list[dict]
        [{"class": str, "confidence": float, "bbox": [x1,y1,x2,y2]}, ...]
    """
    model = _get_model()

    results = model.predict(
        source=image_path,
        conf=0.25,
        imgsz=1024,
    )

    detections = []
    for box in results[0].boxes:
        detections.append({
            "class":      model.names[int(box.cls)],
            "confidence": float(box.conf),
            "bbox":       box.xyxy.tolist()[0],
        })

    return detections
