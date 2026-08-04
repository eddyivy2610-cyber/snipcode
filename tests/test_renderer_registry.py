"""
tests/test_renderer_registry.py
================================
Unit test for RendererRegistry and individual component renderers.
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.renderers.registry import RendererRegistry
from app.services.renderers.base import RenderContext, BaseRenderer
from app.services.renderers.form import FormRenderer
from app.services.renderers.field import FieldRenderer
from app.services.renderers.button import ButtonRenderer
from app.services.renderers.divider import DividerRenderer
from app.services.renderers.inline import InlineActionRenderer
from app.services.renderers.default import DefaultRenderer
from app.services.generator import generate_from_ir
from app.services.semantic_ir import build_semantic_ir
from app.services.layout import build_layout


class CustomWidgetRenderer(BaseRenderer):
    """Custom test renderer to verify runtime strategy registration."""
    def render(self, comp: dict, indent: int, registry: str, ctx: RenderContext) -> str:
        sp = "  " * indent
        return f'{sp}<custom-widget id="{comp.get("id")}">{comp.get("content", {}).get("text")}</custom-widget>'


def test_renderer_registry():
    # 1. Strategy Lookup Test
    assert isinstance(RendererRegistry.get("Form"), FormRenderer), "Form strategy lookup failed!"
    assert isinstance(RendererRegistry.get("Input"), FieldRenderer), "Input strategy lookup failed!"
    assert isinstance(RendererRegistry.get("Button"), ButtonRenderer), "Button strategy lookup failed!"
    assert isinstance(RendererRegistry.get("Divider"), DividerRenderer), "Divider strategy lookup failed!"
    assert isinstance(RendererRegistry.get("InlineAction"), InlineActionRenderer), "InlineAction strategy lookup failed!"
    assert isinstance(RendererRegistry.get("UnknownWidget"), DefaultRenderer), "Fallback strategy lookup failed!"

    # 2. Runtime Custom Strategy Registration Test
    RendererRegistry.register("CustomWidget", CustomWidgetRenderer())
    assert isinstance(RendererRegistry.get("CustomWidget"), CustomWidgetRenderer), "Runtime registration failed!"

    custom_html = RendererRegistry.render({
        "id": "widget_01",
        "type": "CustomWidget",
        "content": {"text": "Custom Element"}
    })
    assert '<custom-widget id="widget_01">Custom Element</custom-widget>' in custom_html

    # 3. Full IR Pipeline Test with RendererRegistry
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

    tree = build_layout(components)
    ir = build_semantic_ir(tree)
    html, css = generate_from_ir(ir)

    assert 'id="form_create_account"' in html
    assert 'id="field_email_address"' in html
    assert 'id="btn_google"' in html
    assert 'data-action="submit_google"' in html
    assert 'class="btn-icon">🌐</span>' in html

    print("\n[OK] test_renderer_registry PASSED!")


if __name__ == "__main__":
    test_renderer_registry()
