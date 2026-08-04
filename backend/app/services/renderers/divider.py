"""
renderers/divider.py
====================
Divider Component Renderer.
"""

from __future__ import annotations
from typing import Dict, Any
from app.services.renderers.base import BaseRenderer, RenderContext, _cls, _spacing_to_mb_class


class DividerRenderer(BaseRenderer):
    """Renders text horizontal dividers (e.g. --- OR ---)."""

    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        sp_str = "  " * indent
        comp_id = comp.get("id", "divider")
        content = comp.get("content", {})
        layout = comp.get("layout", {})

        txt = content.get("text", "or")
        spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
        mb_cls = _spacing_to_mb_class(spacing_val)
        div_cls = _cls("divider", mb_cls)

        return f'{sp_str}<div id="{comp_id}" class="{div_cls}"><span>{txt}</span></div>'
