"""
tests/test_design_system_ir_v4.py
==================================
Unit test for 4-Pillar Design-System IR (v4.0) Compiler & Renderer.
"""

import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.layout import build_layout
from app.services.semantic_ir import build_semantic_ir
from app.services.generator import generate_from_ir


def test_design_system_ir_v4():
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

    # 1. Build layout tree
    tree = build_layout(components)

    # 2. Compile to 4-Pillar Design-System IR v4.0
    ir = build_semantic_ir(tree)

    print("--- 4-Pillar Design-System IR v4.0 JSON ---")
    print(json.dumps(ir, indent=2))

    # 3. Render HTML
    html, css = generate_from_ir(ir)

    # Assertions
    assert ir["schema_version"] == "4.0", "Schema version must be 4.0!"
    form_comp = ir["components"][0]
    assert form_comp["type"] == "Form", "Root container must be Form!"
    assert form_comp["id"] == "form_create_account", "Form ID mismatch!"
    assert "content" in form_comp, "Content pillar missing!"
    assert "layout" in form_comp, "Layout pillar missing!"
    assert "style" in form_comp, "Style pillar missing!"
    assert "behavior" in form_comp, "Behavior pillar missing!"

    # Check child 4-pillar nodes
    pwd_field = next(c for c in form_comp["children"] if c["id"] == "field_password")
    assert pwd_field["content"]["label"] == "Password", "Label missing from content pillar!"
    assert pwd_field["content"]["icon"] == "eye", "Eye icon missing from content pillar!"
    assert pwd_field["layout"]["margin_bottom"] == 30, "Margin bottom missing from layout pillar!"
    assert pwd_field["style"]["corner_radius"] == "medium", "Corner radius missing from style pillar!"
    assert pwd_field["behavior"]["action"] == "input_password", "Behavior action missing!"

    google_btn = next(c for c in form_comp["children"] if c["id"] == "btn_google")
    assert google_btn["variant"] == "oauth", "Variant mismatch!"
    assert google_btn["content"]["icon"] == "google", "Google icon missing from content pillar!"
    assert google_btn["behavior"]["action"] == "submit_google", "Behavior action submit_google missing!"

    # Check HTML output for data-action attributes
    assert 'data-action="submit_google"' in html, "HTML missing data-action='submit_google'!"
    assert 'data-action="submit_form"' in html, "HTML missing data-action='submit_form'!"
    assert 'id="form_create_account"' in html, "HTML missing form id attribute!"

    print("\n[OK] test_design_system_ir_v4 PASSED!")
    print("\n--- Generated HTML Output Preview ---")
    print(html.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    test_design_system_ir_v4()
