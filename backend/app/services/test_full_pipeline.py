"""
services/test_full_pipeline.py
==============================
Runs the full Sensor Fusion + AST Validator backend pipeline on a test screenshot
and outputs the complete JSON result.
"""

import json
import os
from app.services.fusion import fuse_sensors
from app.services.cleaner import clean_detections
from app.services.layout import build_layout
from app.services.validator import validate_ir
from app.services.generator import generate


def run_test(image_path: str):
    print(f"=== Full Backend Pipeline Test: {image_path} ===")

    # 1. Sensor Fusion
    fused_comps = fuse_sensors(image_path)

    # 2. Cleanup & Layout Reconstruction
    comps = clean_detections(fused_comps, img_width=1366, img_height=768)
    tree = build_layout(comps)

    # 3. AST Validator & Linter
    validated_tree, validation_report = validate_ir(tree)

    # 4. Generator
    draft_html, draft_css = generate(validated_tree)

    result = {
        "metadata": {
            "source_image": os.path.basename(image_path),
            "pipeline_version": "v4.1.0-Fusion-Validator",
            "total_components": len(comps),
        },
        "validation_report": validation_report,
        "components": comps,
        "tree": validated_tree,
        "draft_html_sample": draft_html[:300] + "...",
    }

    out_path = "full_pipeline_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"SUCCESS! Output saved to {out_path}")
    return result


if __name__ == "__main__":
    test_img = "uploads/Screenshot (19).png"
    if not os.path.exists(test_img):
        test_img = "backend/uploads/Screenshot (19).png"

    if os.path.exists(test_img):
        run_test(test_img)
    else:
        print(f"Image not found at {test_img}")
