"""
renderers/inline.py
===================
Inline Action Link Component Renderer.
"""

from __future__ import annotations
from typing import Dict, Any
from app.services.renderers.base import BaseRenderer, RenderContext, _cls, _spacing_to_mb_class


class InlineActionRenderer(BaseRenderer):
    """Renders co-located text paragraph + hyperlink action pairs."""

    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        sp_str = "  " * indent
        comp_id = comp.get("id", "inline_action")

        content = comp.get("content", {})
        layout = comp.get("layout", {})
        behavior = comp.get("behavior", {})

        txt = content.get("text", "Already have an account?")
        l_txt = content.get("link_text", "Log In")

        spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
        mb_cls = _spacing_to_mb_class(spacing_val)
        inline_cls = _cls("inline-action", mb_cls)

        action_attr = f' data-action="{behavior["action"]}"' if behavior.get("action") else ""

        return f'{sp_str}<p id="{comp_id}" class="{inline_cls}"{action_attr}>{txt} <a href="#" class="nav-link">{l_txt}</a></p>'
