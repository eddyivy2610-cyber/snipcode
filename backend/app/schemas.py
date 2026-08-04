from pydantic import BaseModel, Field


class Detection(BaseModel):
    """Raw YOLO detection (output of services/detector.py)."""
    class_name:       str
    confidence:       float
    bbox:             list[float]
    text:             str   = Field(default="",  description="OCR text from the detected region")
    text_confidence:  float = Field(default=0.0, description="OCR confidence score (0–1)")


class Component(BaseModel):
    """
    Merged detection + OCR result — the canonical unit of the layout engine.

    Produced by services/merger.py and consumed by services/layout.py.
    """
    type:             str
    bbox:             list[float]
    confidence:       float
    text:             str   = ""
    text_confidence:  float = 0.0
    children:         list  = Field(default_factory=list)