"""
tests/test_semantic_ir.py
==========================
Unit test for Intermediate Representation (IR) compiler and utility class spacing.
"""

import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.layout import build_layout
from app.services.semantic_ir import build_semantic_ir
from app.services.generator import generate_from_ir, generate


def test_semantic_ir_compiler():
    components = [
        {"type": "Text", "bbox": [150, 100, 350, 130], "confidence": 0.98, "text": "Create Account"},
        {"type": "Text", "bbox": [150, 160, 220, 180], "confidence": 0.92, "text": "Email Address"},
        {"type": "Input", "bbox": [150, 185, 450, 225], "confidence": 0.96, "text": ""},
        {"type": "Text", "bbox": [150, 245, 220, 265], "confidence": 0.92, "text": "Password"},
        {"type": "Input", "bbox": [150, 270, 450, 310], "confidence": 0.96, "text": ""},
        {"type": "Button", "bbox": [150, 340, 450, 385], "confidence": 0.97, "text": "Sign Up"},
        {"type": "Text", "bbox": [280, 410, 320, 430], "confidence": 0.95, "text": "OR"},
        {"type": "Button", "bbox": [150, 450, 450, 495], "confidence": 0.97, "text": "Sign up with Google"},
    ]

    # 1. Build layout tree with utility spacing classes
    tree = build_layout(components)

    # 2. Compile to Intermediate Semantic IR
    ir = build_semantic_ir(tree)

    print("--- Intermediate Semantic IR JSON ---")
    print(json.dumps(ir, indent=2))

    # 3. Render HTML from IR
    html_from_ir, css = generate_from_ir(ir)

    # 4. Assertions
    assert ir["schema_version"] == "2.0", "Invalid schema version!"
    comp = ir["components"][0]
    assert comp["type"] == "Form", "Form component missing from IR!"
    assert len(comp["fields"]) == 2, "Fields count mismatch in IR!"
    assert comp["fields"][0]["label"] == "Email Address", "Field label mismatch!"
    assert comp["fields"][1]["trailing_icon"] == "eye", "Password trailing icon missing or incorrect!"
    assert comp["fields"][0]["layout"]["spacing_after"] == 45, "Layout spacing_after missing!"
    assert any(a["kind"] == "oauth" and a.get("leading_icon") == "google" for a in comp["actions"]), "Google OAuth action or leading icon missing in IR!"

    # Assert no inline margin styles in HTML output
    assert "style=\"margin-bottom:" not in html_from_ir, "Inline styles found in HTML output!"
    assert "mb-" in html_from_ir, "Utility margin classes missing from HTML output!"

    print("\n[OK] test_semantic_ir_compiler PASSED!")
    print("\n--- Generated HTML Preview from Semantic IR ---")
    print(html_from_ir.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    test_semantic_ir_compiler()
