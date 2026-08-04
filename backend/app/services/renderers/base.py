"""
renderers/base.py
=================
Abstract Base Renderer interface and RenderContext for Snipcode.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class RenderContext:
    """Lightweight rendering context passing theme, target framework, and options."""
    def __init__(self, target_framework: str = "html", theme: str = "dark"):
        self.target_framework = target_framework
        self.theme = theme


def _spacing_to_mb_class(spacing: int | None) -> str:
    """Map vertical spacing in pixels to standard reusable CSS utility class."""
    if not spacing:
        return ""
    if spacing <= 10:
        return "mb-8"
    elif spacing <= 14:
        return "mb-12"
    elif spacing <= 18:
        return "mb-16"
    elif spacing <= 22:
        return "mb-20"
    elif spacing <= 28:
        return "mb-24"
    elif spacing <= 34:
        return "mb-32"
    elif spacing <= 38:
        return "mb-36"
    elif spacing <= 44:
        return "mb-40"
    else:
        return "mb-48"


def _cls(base_cls: str, mb_cls: str) -> str:
    """Join base CSS class with optional margin utility class."""
    return f"{base_cls} {mb_cls}".strip() if mb_cls else base_cls


class BaseRenderer(ABC):
    """Abstract Base Class for all Component Renderers."""

    @abstractmethod
    def render(self, comp: dict[str, Any], indent: int, registry: Any, ctx: RenderContext) -> str:
        """
        Render component dictionary to target HTML string representation.
        """
        pass
