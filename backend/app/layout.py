"""
layout.py — compatibility shim
================================
The layout engine now lives in app/services/layout.py.
Re-exports `build_layout` (new name) and provides a thin adapter
`build_layout_tree` so legacy callers still work.
"""

from app.services.layout import (   # noqa: F401
    build_layout,
    sort_components,
    inside,
    build_tree,
    same_row,
    same_column,
    group_layout,
)


def build_layout_tree(detections, img_width=800, img_height=600):
    """
    Adapter for legacy callers that pass ``class_name`` dicts.

    Normalises each detection to have ``type`` (from ``class_name``) and
    delegates to the new ``build_layout``.
    """
    comps = []
    for d in detections:
        comps.append({
            "type":             d.get("class_name", d.get("class", "Unknown")),
            "bbox":             d.get("bbox", [0, 0, 0, 0]),
            "confidence":       d.get("confidence", 1.0),
            "text":             d.get("text", ""),
            "text_confidence":  d.get("text_confidence", 0.0),
            "children":         [],
        })
    return build_layout(comps)


__all__ = [
    "build_layout",
    "build_layout_tree",
    "sort_components",
    "inside",
    "build_tree",
    "same_row",
    "same_column",
    "group_layout",
]
