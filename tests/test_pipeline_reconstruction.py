"""
tests/test_pipeline_reconstruction.py
=======================================
Unit test verifying pipeline improvements:
- Desktop/Browser noise filtering
- Label-Input pairing
- Same-row Text + Link inline action merging
- Synthetic Card/Form clustering
- Semantic HTML generation
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.cleaner import clean_detections
from app.services.layout import (
    merge_labels_and_inputs,
    merge_inline_text_actions,
    build_layout
)
from app.services.generator import generate


def test_desktop_noise_filtering():
    raw_detections = [
        {"class": "Text", "bbox": [10, 10, 80, 30], "confidence": 0.95, "text": "File"},
        {"class": "Text", "bbox": [100, 10, 350, 35], "confidence": 0.95, "text": "http://localhost:8000/app.html"},
        {"class": "Text", "bbox": [10, 750, 60, 780], "confidence": 0.95, "text": "ENG"},
        {"class": "Text", "bbox": [150, 150, 350, 180], "confidence": 0.98, "text": "Sign Up"},
        {"class": "Text", "bbox": [150, 200, 220, 220], "confidence": 0.92, "text": "Name"},
        {"class": "Input", "bbox": [150, 225, 450, 265], "confidence": 0.96, "text": ""},
        {"class": "Button", "bbox": [150, 300, 450, 345], "confidence": 0.97, "text": "Sign Up Button"},
    ]

    cleaned = clean_detections(
        components=raw_detections,
        img_width=800,
        img_height=800
    )

    texts = [c["text"] for c in cleaned]
    assert "File" not in texts, "Browser noise 'File' was not filtered!"
    assert "http://localhost:8000/app.html" not in texts, "Browser address bar URL was not filtered!"
    assert "ENG" not in texts, "Taskbar tray icon 'ENG' was not filtered!"
    assert "Sign Up" in texts, "Valid UI text 'Sign Up' was incorrectly filtered!"
    print("[OK] test_desktop_noise_filtering PASSED")


def test_label_and_inline_action_pairing():
    components = [
        {"type": "Text", "bbox": [150, 150, 350, 180], "confidence": 0.98, "text": "Sign Up"},
        {"type": "Text", "bbox": [150, 200, 220, 220], "confidence": 0.92, "text": "Name"},
        {"type": "Input", "bbox": [150, 225, 450, 265], "confidence": 0.96, "text": ""},
        {"type": "Button", "bbox": [150, 300, 450, 345], "confidence": 0.97, "text": "Create Account"},
        {"type": "Text", "bbox": [150, 360, 320, 380], "confidence": 0.91, "text": "Already have an account?"},
        {"type": "Link", "bbox": [330, 360, 400, 380], "confidence": 0.93, "text": "Log In"},
    ]

    tree = build_layout(components)
    html, css = generate(tree)

    # Assertions
    assert "form-card" in html or "card" in html, "Card panel wrapper was not generated!"
    assert "form-group" in html, "Form group wrapper for labeled input was not generated!"
    assert '<label class="form-label">Name</label>' in html, "Input label 'Name' was not correctly paired!"
    assert "inline-action" in html, "Inline action paragraph was not generated!"
    assert "Already have an account?" in html and "Log In" in html, "Inline action text/link missing!"

    print("[OK] test_label_and_inline_action_pairing PASSED")
    print("\n--- Generated HTML Output Preview ---")
    print(html)


if __name__ == "__main__":
    test_desktop_noise_filtering()
    test_label_and_inline_action_pairing()
    print("\nALL PIPELINE RECONSTRUCTION TESTS PASSED SUCCESSFULLY!")
