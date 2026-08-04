"""
renderers/default.py
====================
Fallback Default Renderer for custom/unregistered components.
"""

from __future__ import annotations
from typing import Dict, Any
from app.services.renderers.base import BaseRenderer, RenderContext, _cls, _spacing_to_mb_class


class DefaultRenderer(BaseRenderer):
    """Fallback renderer that safely renders unknown nodes without crashing."""

    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        sp_str = "  " * indent
        comp_id = comp.get("id", "comp")
        c_type = comp.get("type", "div").lower()
        content = comp.get("content", {})
        layout = comp.get("layout", {})
        children = comp.get("children", [])

        txt = content.get("text", "")
        spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
        mb_cls = _spacing_to_mb_class(spacing_val)
        elem_cls = _cls("text-content", mb_cls)

        if children:
            lines = [f'{sp_str}<div id="{comp_id}" class="{elem_cls}">']
            for child in children:
                c_html = registry.render(child, indent + 1, ctx)
                if c_html:
                    lines.append(c_html)
            lines.append(f'{sp_str}</div>')
            return "\n".join(lines)

        return f'{sp_str}<div id="{comp_id}" class="{elem_cls}">{txt}</div>'
