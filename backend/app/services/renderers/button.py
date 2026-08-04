"""
renderers/button.py
===================
Button Component Renderer.
"""

from __future__ import annotations
from typing import Dict, Any
from app.services.renderers.base import BaseRenderer, RenderContext, _cls, _spacing_to_mb_class
from app.services.renderers.icons import resolve_icon


class ButtonRenderer(BaseRenderer):
    """Renders Button components (Primary, Secondary, OAuth) with brand icon badges."""

    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        sp_str = "  " * indent
        comp_id = comp.get("id", "btn")

        content = comp.get("content", {})
        layout = comp.get("layout", {})
        behavior = comp.get("behavior", {})

        txt = content.get("text", "Submit")
        icon_name = content.get("icon") or comp.get("leading_icon")

        spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
        mb_cls = _spacing_to_mb_class(spacing_val)
        btn_cls = _cls("btn", mb_cls)

        action_attr = f' data-action="{behavior["action"]}"' if behavior.get("action") else ""

        icon_symbol = resolve_icon(icon_name, "🌐" if comp.get("variant") == "oauth" else "")
        icon_prefix = f'<span class="btn-icon">{icon_symbol}</span> ' if icon_symbol else ""

        return f'{sp_str}<button id="{comp_id}" class="{btn_cls}"{action_attr}>{icon_prefix}{txt}</button>'
