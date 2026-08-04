"""
tests/test_theme_engine.py
===========================
Unit test for Design System & Theme Engine (theme.py).
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.theme import ThemeRegistry, map_to_tailwind
from app.services.renderers.base import RenderContext
from app.services.generator import generate_from_ir
from app.services.semantic_ir import build_semantic_ir
from app.services.layout import build_layout


def test_theme_engine():
    # 1. Preset Lookup Test
    dark = ThemeRegistry.get_theme("dark")
    light = ThemeRegistry.get_theme("light")
    blue = ThemeRegistry.get_theme("cyber_blue")

    assert dark.bg_page == "#090d13", "Dark theme background mismatch!"
    assert light.bg_page == "#f6f8fa", "Light theme background mismatch!"
    assert blue.bg_page == "#030712", "Cyber blue theme background mismatch!"

    # 2. CSS Custom Properties Compilation Test
    dark_css = ThemeRegistry.get_theme_css("dark")
    light_css = ThemeRegistry.get_theme_css("light")

    assert ":root {" in dark_css, "CSS Custom Properties root block missing!"
    assert "--bg-page: #090d13;" in dark_css, "Dark theme CSS variable missing!"
    assert "--bg-page: #f6f8fa;" in light_css, "Light theme CSS variable missing!"

    # 3. Dynamic Multi-Theme Generation Test
    components = [
        {"type": "Text", "bbox": [150, 100, 350, 130], "confidence": 0.98, "text": "Create Account"},
        {"type": "Text", "bbox": [150, 160, 220, 180], "confidence": 0.92, "text": "Email Address"},
        {"type": "Input", "bbox": [150, 185, 450, 225], "confidence": 0.96, "text": ""},
        {"type": "Button", "bbox": [150, 340, 450, 385], "confidence": 0.97, "text": "Sign Up"},
    ]

    tree = build_layout(components)
    ir = build_semantic_ir(tree)

    # Dark Theme Render
    html_dark, css_dark = generate_from_ir(ir, ctx=RenderContext(theme="dark"))
    assert 'data-theme="dark"' in html_dark
    assert "--bg-page: #090d13;" in css_dark

    # Light Theme Render
    html_light, css_light = generate_from_ir(ir, ctx=RenderContext(theme="light"))
    assert 'data-theme="light"' in html_light
    assert "--bg-page: #f6f8fa;" in css_light

    # Cyber Blue Theme Render
    html_blue, css_blue = generate_from_ir(ir, ctx=RenderContext(theme="cyber_blue"))
    assert 'data-theme="cyber_blue"' in html_blue
    assert "--bg-page: #030712;" in css_blue

    # 4. Tailwind Utility Mapping Test
    tw_card = map_to_tailwind("card")
    assert "bg-slate-900" in tw_card, "Tailwind card mapping failed!"

    print("\n[OK] test_theme_engine PASSED!")


if __name__ == "__main__":
    test_theme_engine()
