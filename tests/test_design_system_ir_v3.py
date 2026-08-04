"""
tests/test_design_system_ir_v3.py
==================================
Unit test for Design-System IR (v3.0) Compiler and Renderer.
"""

import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.layout import build_layout
from app.services.semantic_ir import build_semantic_ir
from app.services.generator import generate_from_ir


def test_design_system_ir_v3():
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

    # 2. Compile to Design-System IR v3.0
    ir = build_semantic_ir(tree)

    print("--- Design-System IR v3.0 JSON ---")
    print(json.dumps(ir, indent=2))

    # 3. Render HTML
    html, css = generate_from_ir(ir)

    # Assertions
    assert ir["schema_version"] == "3.0", "Schema version must be 3.0!"
    form_comp = ir["components"][0]
    assert form_comp["type"] == "Form", "Root container must be Form!"
    assert form_comp["id"] == "form_create_account", "Form ID mismatch!"
    assert len(form_comp["children"]) == 5, "Form children count mismatch!"

    # Check child nodes
    child_ids = [c["id"] for c in form_comp["children"]]
    assert "field_email_address" in child_ids, "Field email_address ID missing!"
    assert "field_password" in child_ids, "Field password ID missing!"
    assert "btn_sign_up" in child_ids, "Button sign_up ID missing!"
    assert "divider_or" in child_ids, "Divider or ID missing!"
    assert "btn_google" in child_ids, "Button google OAuth ID missing!"

    # Check content, variant, layout decoupling
    pwd_field = next(c for c in form_comp["children"] if c["id"] == "field_password")
    assert pwd_field["content"]["label"] == "Password", "Label missing from content block!"
    assert pwd_field["trailing_icon"] == "eye", "Trailing icon missing!"
    assert pwd_field["layout"]["margin_bottom"] == 30, "Layout margin_bottom missing!"

    oauth_btn = next(c for c in form_comp["children"] if c["id"] == "btn_google")
    assert oauth_btn["variant"] == "oauth", "Variant mismatch!"
    assert oauth_btn["content"]["icon"] == "google", "Content icon mismatch!"

    # Check HTML output for IDs and utility classes
    assert 'id="form_create_account"' in html, "HTML missing form id attribute!"
    assert 'id="field_email_address"' in html, "HTML missing field_email_address id attribute!"
    assert 'id="btn_google"' in html, "HTML missing btn_google id attribute!"
    assert 'mb-' in html, "HTML missing utility class spacing!"

    print("\n[OK] test_design_system_ir_v3 PASSED!")
    print("\n--- Generated HTML Output Preview ---")
    print(html.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    test_design_system_ir_v3()
