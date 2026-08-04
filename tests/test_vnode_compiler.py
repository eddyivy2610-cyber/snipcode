"""
tests/test_vnode_compiler.py
=============================
Unit test for Virtual UI Tree (VNode AST) Compiler and Multi-Target Serializers.
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.vnode import build_vnode_tree, HTMLSerializer, ReactSerializer, FlutterSerializer
from app.services.semantic_ir import build_semantic_ir
from app.services.layout import build_layout


def test_vnode_compiler():
    components = [
        {"type": "Text", "bbox": [150, 100, 350, 130], "confidence": 0.98, "text": "Create Account"},
        {"type": "Text", "bbox": [150, 160, 220, 180], "confidence": 0.92, "text": "Email Address"},
        {"type": "Input", "bbox": [150, 185, 450, 225], "confidence": 0.96, "text": ""},
        {"type": "Button", "bbox": [150, 340, 450, 385], "confidence": 0.97, "text": "Sign Up"},
    ]

    # 1. Build layout tree & IR v4.0
    tree = build_layout(components)
    ir = build_semantic_ir(tree)

    # 2. Build VNode AST Tree
    vnode_roots = build_vnode_tree(ir)
    assert len(vnode_roots) == 1, "VNode root count mismatch!"
    form_vnode = vnode_roots[0]
    assert form_vnode.tag == "form", "Root VNode tag mismatch!"
    assert form_vnode.id == "form_create_account", "Root VNode ID mismatch!"

    # 3. HTML Serializer Verification
    html_code = HTMLSerializer.serialize(form_vnode, indent=1)
    assert '<form id="form_create_account" class="card form-card"' in html_code
    assert '<h2 class="container-title mb-24">Create Account</h2>' in html_code
    assert 'class="form-input"' in html_code

    # 4. React JSX Serializer Verification
    react_code = ReactSerializer.serialize(form_vnode, indent=1)
    assert 'className="card form-card"' in react_code, "React className attribute missing!"
    assert '<input className="form-input" type="email" placeholder="Enter email address" />' in react_code, "React input JSX missing!"

    # 5. Flutter Serializer Verification
    flutter_code = FlutterSerializer.serialize(form_vnode, indent=1)
    assert 'TextFormField(' in flutter_code, "Flutter TextFormField widget missing!"
    assert 'ElevatedButton(' in flutter_code, "Flutter ElevatedButton widget missing!"

    print("\n[OK] test_vnode_compiler PASSED!")
    print("\n--- Generated React JSX Output ---")
    print(react_code)
    print("\n--- Generated Flutter Widget Output ---")
    print(flutter_code)


if __name__ == "__main__":
    test_vnode_compiler()
