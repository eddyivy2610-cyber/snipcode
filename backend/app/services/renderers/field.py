"""
renderers/field.py
==================
Field and Input Component Renderer.
"""

from __future__ import annotations
from typing import Dict, Any
from app.services.renderers.base import BaseRenderer, RenderContext, _cls, _spacing_to_mb_class
from app.services.renderers.icons import resolve_icon


class FieldRenderer(BaseRenderer):
    """Renders Input field components with labels and trailing/leading icon badges."""

    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        sp_str = "  " * indent
        comp_id = comp.get("id", "input_field")
        i_type = comp.get("input_type", "text")

        content = comp.get("content", {})
        layout = comp.get("layout", {})
        behavior = comp.get("behavior", {})

        lbl = content.get("label", "")
        pl = content.get("placeholder", "")
        icon_name = content.get("icon") or comp.get("trailing_icon")

        spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
        mb_cls = _spacing_to_mb_class(spacing_val)
        group_cls = _cls("form-group", mb_cls)

        action_attr = f' data-action="{behavior["action"]}"' if behavior.get("action") else ""

        icon_symbol = resolve_icon(icon_name, "👁️" if i_type == "password" else "")
        icon_html = f' <span class="input-icon">{icon_symbol}</span>' if icon_symbol else ""

        lines = [f'{sp_str}<div id="{comp_id}" class="{group_cls}"{action_attr}>']
        if lbl:
            lines.append(f'{sp_str}  <label class="form-label">{lbl}</label>')
        lines.append(f'{sp_str}  <div class="input-wrapper">')
        lines.append(f'{sp_str}    <input type="{i_type}" class="form-input" placeholder="{pl}" />{icon_html}')
        lines.append(f'{sp_str}  </div>')
        lines.append(f'{sp_str}</div>')

        return "\n".join(lines)
