"""
tests/test_phase2_layout.py
============================
Unit test verifying Phase 2 layout engine features:
- Field node abstraction
- Input wrapper & eye icon rendering
- Divider detection ("or")
- Social button icon badges
- Dynamic bounding-box margin calculation
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.layout import build_layout
from app.services.generator import generate


def test_phase2_features():
    components = [
        {"type": "Text", "bbox": [150, 100, 350, 130], "confidence": 0.98, "text": "Create Account"},
        {"type": "Text", "bbox": [150, 160, 220, 180], "confidence": 0.92, "text": "Email Address"},
        {"type": "Input", "bbox": [150, 185, 450, 225], "confidence": 0.96, "text": ""},
        {"type": "Text", "bbox": [150, 245, 220, 265], "confidence": 0.92, "text": "Password"},
        {"type": "Input", "bbox": [150, 270, 450, 310], "confidence": 0.96, "text": ""},
        {"type": "Icon", "bbox": [420, 280, 440, 300], "confidence": 0.90, "text": "eye"},
        {"type": "Button", "bbox": [150, 340, 450, 385], "confidence": 0.97, "text": "Sign Up"},
        {"type": "Text", "bbox": [280, 410, 320, 430], "confidence": 0.95, "text": "OR"},
        {"type": "Button", "bbox": [150, 450, 450, 495], "confidence": 0.97, "text": "Sign up with Google"},
    ]

    tree = build_layout(components)
    html, css = generate(tree)

    print("--- Reconstructed Tree Types ---")
    def print_types(nodes, depth=0):
        for n in nodes:
            t = n.get("type")
            txt = n.get("text", "")
            lbl = n.get("label", "")
            mb = n.get("margin_bottom")
            mb_str = f" [margin_bottom: {mb}px]" if mb else ""
            print("  " * depth + f"- {t} (text: '{txt}', label: '{lbl}'){mb_str}")
            if n.get("children"):
                print_types(n["children"], depth + 1)
    print_types(tree)

    # Assertions
    assert "divider" in html, "Divider element was not generated!"
    assert "<span>OR</span>" in html or "<span>or</span>" in html, "Divider text missing!"
    assert 'class="btn-icon"' in html, "Social button icon was not rendered!"
    assert 'class="input-icon"' in html or '👁️' in html, "Input eye icon was not rendered!"
    assert "style=\"margin-bottom:" in html, "Dynamic bounding box margin spacing was not injected!"

    print("\n[OK] test_phase2_features PASSED!")
    print("\n--- Generated HTML Output Preview ---")
    print(html.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    test_phase2_features()
