"""
services/compare_phase2.py
==========================
Phase 2 — Output Comparison Service.

Generates side-by-side YOLO JSON vs ScreenParser JSON outputs for a single screenshot
to inspect exact semantic differences without merging.
"""

import json
import os
from app.services.detector import detect
from app.services.screenparser import parse_screen


def compare_outputs(image_path: str):
    print(f"=== Phase 2: Comparing Outputs for {image_path} ===")

    # 1. Generate Raw YOLO JSON
    raw_yolo_dets = detect(image_path)
    yolo_json = {
        "metadata": {
            "source_image": os.path.basename(image_path),
            "engine": "YOLOv8",
            "total_elements": len(raw_yolo_dets),
        },
        "components": [
            {
                "type": d["class"],
                "bbox": d["bbox"],
                "confidence": round(d["confidence"], 2),
            }
            for d in raw_yolo_dets
        ],
    }

    # Save yolo.json
    yolo_out_path = "yolo_output.json"
    with open(yolo_out_path, "w", encoding="utf-8") as f:
        json.dump(yolo_json, f, indent=2)

    # 2. Generate ScreenParser JSON
    screenparser_json = parse_screen(image_path, output_json_path="screenparser_output.json")

    print("\n--- YOLO JSON Sample (First 2 Elements) ---")
    print(json.dumps(yolo_json["components"][:2], indent=2))

    print("\n--- ScreenParser JSON Sample (First 2 Elements) ---")
    print(json.dumps(screenparser_json["components"][:2], indent=2))

    return yolo_json, screenparser_json


if __name__ == "__main__":
    test_img = "uploads/Screenshot (19).png"
    if not os.path.exists(test_img):
        test_img = "backend/uploads/Screenshot (19).png"

    if os.path.exists(test_img):
        compare_outputs(test_img)
    else:
        print(f"Image not found at {test_img}")
