"""
generator.py — compatibility shim
===================================
The HTML/CSS generator now lives in app/services/generator.py.
Re-exports `generate` and keeps the legacy `CodeGenerator` class
as a thin wrapper for backwards compatibility.
"""

from app.services.generator import generate  # noqa: F401


class CodeGenerator:
    """
    Legacy wrapper kept for backwards compatibility.

    New code should call ``app.services.generator.generate(tree)`` directly.
    """

    def generate(self, tree) -> tuple[str, str]:
        # If tree is a LayoutNode (old engine), convert to dict first
        if hasattr(tree, "to_dict"):
            tree = [tree.to_dict()]
        elif isinstance(tree, dict):
            tree = [tree]
        return generate(tree)


__all__ = ["generate", "CodeGenerator"]
