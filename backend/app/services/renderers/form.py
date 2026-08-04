"""
renderers/form.py
=================
Form and Card Container Renderer.
"""

from __future__ import annotations
from typing import Dict, Any
from app.services.renderers.base import BaseRenderer, RenderContext, _cls, _spacing_to_mb_class


class FormRenderer(BaseRenderer):
    """Renders Form / Card container nodes and recursively delegates child rendering."""

    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        sp_str = "  " * indent
        comp_id = comp.get("id", "form_container")
        content = comp.get("content", {})
        layout = comp.get("layout", {})
        behavior = comp.get("behavior", {})
        children = comp.get("children", [])

        title = content.get("title", "Sign Up")
        spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
        mb_cls = _spacing_to_mb_class(spacing_val)
        card_cls = _cls("card form-card", mb_cls)

        action_attr = f' data-action="{behavior["action"]}"' if behavior.get("action") else ""

        lines = [f'{sp_str}<form id="{comp_id}" class="{card_cls}"{action_attr}>']
        if title:
            lines.append(f'{sp_str}  <h2 class="container-title mb-24">{title}</h2>')

        for child in children:
            child_html = registry.render(child, indent + 1, ctx)
            if child_html:
                lines.append(child_html)

        lines.append(f'{sp_str}</form>')
        return "\n".join(lines)
