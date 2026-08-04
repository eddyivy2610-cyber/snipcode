"""
tests/test_screenshot19.py
===========================
Runs the full Snipcode pipeline on backend/uploads/Screenshot (19).png
and logs raw detections, cleaned components, reconstructed tree, and final HTML.
"""

import sys
import os
import json
from PIL import Image

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.detector import detect
from app.services.merger import merge
from app.services.cleaner import clean_detections
from app.services.layout import build_layout
from app.services.generator import generate

def main():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "uploads", "Screenshot (19).png"))
    print(f"Testing on image: {img_path}")

    if not os.path.exists(img_path):
        print(f"ERROR: Image file not found at {img_path}")
        return

    # Image dimensions
    with Image.open(img_path) as img:
        w, h = img.size
    print(f"Image dimensions: {w}x{h}")

    # 1. YOLO Detection
    print("\n--- Step 1: Running YOLO detector ---")
    raw_detections = detect(img_path)
    print(f"Raw YOLO detections count: {len(raw_detections)}")
    for d in raw_detections:
        print(f"  - Class: {d['class']}, Confidence: {d['confidence']:.2f}, Box: {[round(x, 1) for x in d['bbox']]}")

    # 2. OCR & Merge
    print("\n--- Step 2: Running EasyOCR & Merger ---")
    merged_components = merge(raw_detections, img_path)
    print(f"Merged components count: {len(merged_components)}")

    # 3. Detection Cleanup & Noise Filtering
    print("\n--- Step 3: Running Cleaner (NMS & Desktop Noise Filtering) ---")
    cleaned_components = clean_detections(merged_components, img_width=w, img_height=h)
    print(f"Cleaned components count: {len(cleaned_components)}")
    for c in cleaned_components:
        text_str = f", Text: '{c['text']}'" if c.get('text') else ""
        label_str = f", Label: '{c['label']}'" if c.get('label') else ""
        print(f"  - Type: {c['type']}, Confidence: {c.get('confidence', 0):.2f}{text_str}{label_str}, Box: {[round(x, 1) for x in c['bbox']]}")

    # 4. Layout Reconstruction
    print("\n--- Step 4: Reconstructing Component Tree ---")
    tree = build_layout(cleaned_components, img_height=h)
    print(f"Reconstructed tree roots count: {len(tree)}")
    print(json.dumps(tree, indent=2))

    # 5. HTML/CSS Generation
    print("\n--- Step 5: Generating HTML & CSS ---")
    html, css = generate(tree)

    os.makedirs("generated", exist_ok=True)
    out_html_path = "generated/screenshot19_output.html"
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nHTML generated successfully! Saved to: {out_html_path}")
    print("\nGenerated HTML Preview:")
    print(html)

if __name__ == "__main__":
    main()
