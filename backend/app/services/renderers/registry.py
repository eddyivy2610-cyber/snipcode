"""
renderers/registry.py
=====================
Central Renderer Registry mapping component types and variants to renderers.
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from app.services.renderers.base import BaseRenderer, RenderContext
from app.services.renderers.form import FormRenderer
from app.services.renderers.field import FieldRenderer
from app.services.renderers.button import ButtonRenderer
from app.services.renderers.divider import DividerRenderer
from app.services.renderers.inline import InlineActionRenderer
from app.services.renderers.default import DefaultRenderer


class RendererRegistry:
    """Central component renderer registry implementing the Strategy Pattern."""

    _registry: dict[str, BaseRenderer] = {
        "form": FormRenderer(),
        "card": FormRenderer(),
        "input": FieldRenderer(),
        "field": FieldRenderer(),
        "button": ButtonRenderer(),
        "divider": DividerRenderer(),
        "inlineaction": InlineActionRenderer(),
        "inline": InlineActionRenderer(),
    }

    _fallback: BaseRenderer = DefaultRenderer()

    @classmethod
    def register(cls, key: str, renderer: BaseRenderer) -> None:
        """Register a new component renderer at runtime."""
        cls._registry[key.lower()] = renderer

    @classmethod
    def get(cls, comp_type: str, variant: str = "") -> BaseRenderer:
        """Lookup renderer by type or variant, falling back to DefaultRenderer."""
        t_key = (comp_type or "").lower()
        v_key = (variant or "").lower()

        if t_key in cls._registry:
            return cls._registry[t_key]
        elif v_key in cls._registry:
            return cls._registry[v_key]

        return cls._fallback

    @classmethod
    def render(cls, comp: dict[str, Any], indent: int = 1, ctx: Optional[RenderContext] = None) -> str:
        """Render component node by resolving its strategy renderer."""
        if ctx is None:
            ctx = RenderContext()

        c_type = comp.get("type", "")
        variant = comp.get("variant", "")

        renderer = cls.get(c_type, variant)
        return renderer.render(comp, indent, cls, ctx)
