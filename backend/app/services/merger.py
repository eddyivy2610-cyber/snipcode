"""
services/merger.py
==================
Merges raw YOLO detections with OCR results to produce Component dicts.

This is the step that was previously smeared across inference.py and main.py.
Having it isolated means you can:
  - unit-test detection and OCR separately
  - swap in a different OCR engine without touching the detector
  - inspect the merged output via /api/layout before HTML generation

Pipeline position:
    detector.detect()  →  merger.merge()  →  layout.build_tree()
"""

from __future__ import annotations

from app.services.ocr import perform_ocr, perform_full_ocr


def refine_component_type(current_type: str, text: str) -> str:
    """Refine element type based on text content hints."""
    lower = text.lower()
    
    # Check for Input field indicators
    if any(k in lower for k in ["password", "email", "search", "enter ", "type "]):
        if current_type in ["Link", "Text"]:
            return "Input"
            
    # Check for Button indicators
    if any(k in lower for k in ["sign up", "sign in", "log in", "submit", "google", "continue", "register", ">", "→", "templates"]):
        if current_type in ["Link", "Text"]:
            return "Button"

    return current_type


def merge(
    detections: list[dict],
    image_path: str,
) -> list[dict]:
    """
    Enrich each raw YOLO detection with OCR text and capture any missed text
    as standalone components (hybrid OCR-based fallback).
    """
    components = []
    
    # 1. Run OCR on the entire image
    ocr_blocks = perform_full_ocr(image_path)
    matched_ocr_indices = set()

    # 2. Enrich YOLO detections with overlapping OCR text blocks
    for det in detections:
        y_xmin, y_ymin, y_xmax, y_ymax = det["bbox"]
        
        # Find OCR blocks whose center lies inside the YOLO bounding box
        intersecting = []
        for idx, block in enumerate(ocr_blocks):
            b_xmin, b_ymin, b_xmax, b_ymax = block["bbox"]
            cx = (b_xmin + b_xmax) / 2
            cy = (b_ymin + b_ymax) / 2
            if y_xmin <= cx <= y_xmax and y_ymin <= cy <= y_ymax:
                intersecting.append(block)
                matched_ocr_indices.add(idx)

        if intersecting:
            # Sort naturally: top-to-bottom, then left-to-right
            intersecting.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
            text = " ".join([b["text"] for b in intersecting])
            text_conf = max(b["confidence"] for b in intersecting)
        else:
            # Fallback to cropping OCR if full-image OCR missed it
            ocr = perform_ocr(image_path, det["bbox"])
            text = ocr["text"]
            text_conf = ocr["confidence"]

        comp_type = refine_component_type(det["class"], text)

        components.append({
            "type":             comp_type,
            "bbox":             [float(v) for v in det["bbox"]],
            "confidence":       float(det["confidence"]),
            "text":             text,
            "text_confidence":  float(text_conf),
            "children":         [],
        })

    # 3. Add unmatched OCR text blocks as standalone components
    for idx, block in enumerate(ocr_blocks):
        if idx in matched_ocr_indices:
            continue

        text_val = block["text"]
        comp_type = refine_component_type("Text", text_val)

        components.append({
            "type":             comp_type,
            "bbox":             block["bbox"],
            "confidence":       block["confidence"],
            "text":             text_val,
            "text_confidence":  block["confidence"],
            "children":         [],
        })

    return components

