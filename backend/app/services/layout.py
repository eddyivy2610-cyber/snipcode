"""
services/layout.py
==================
Layout Reconstruction Engine — Milestone 3.

Transforms a flat list of Component dicts into a hierarchical UI tree
by answering the spatial questions YOLO cannot:

  - Which components belong together?
  - Which items are in the same row / column?
  - Which component contains another?
  - Which Button belongs to which Card?

Pipeline (6 steps)
------------------
1. sort_components  — top→bottom, left→right
2. inside           — strict containment check
3. build_tree       — assign children to smallest containing parent
4. same_row         — Y-centres within tolerance
5. same_column      — X-centres within tolerance
6. group_layout     — wrap detected rows/columns into synthetic nodes

Output example
--------------
[
    {"type": "Toolbar", "children": []},
    {
        "type": "Column",
        "children": [
            {"type": "Input",  "text": "Username"},
            {"type": "Input",  "text": "Password"},
            {"type": "Button", "text": "Login"},
        ]
    },
    {"type": "BottomNavigation", "children": []},
]
"""

from __future__ import annotations

import copy
from typing import Any


# ---------------------------------------------------------------------------
# Step 1 — Sort
# ---------------------------------------------------------------------------

def sort_components(components: list[dict]) -> list[dict]:
    """
    Sort components top→bottom, then left→right within the same row.

    Uses bbox[1] (y-top) as primary key and bbox[0] (x-left) as secondary
    so reading order matches natural document flow.
    """
    return sorted(
        components,
        key=lambda c: (c["bbox"][1], c["bbox"][0]),
    )


# ---------------------------------------------------------------------------
# Step 2 — Containment
# ---------------------------------------------------------------------------

def inside(inner: list[float], outer: list[float], threshold: float = 0.80) -> bool:
    """
    Return True when *inner* bbox is >= *threshold* fraction inside *outer*.

    Uses overlap-area / inner-area instead of strict containment so that
    slight YOLO bbox jitter does not break parent-child assignment.

    Parameters
    ----------
    inner, outer : [x1, y1, x2, y2]
    threshold    : fraction of inner area that must overlap outer (default 80 %)
    """
    ix1, iy1, ix2, iy2 = inner
    ox1, oy1, ox2, oy2 = outer

    # Intersection rectangle
    cx1 = max(ix1, ox1)
    cy1 = max(iy1, oy1)
    cx2 = min(ix2, ox2)
    cy2 = min(iy2, oy2)

    if cx2 <= cx1 or cy2 <= cy1:
        return False

    overlap = (cx2 - cx1) * (cy2 - cy1)
    inner_area = max((ix2 - ix1) * (iy2 - iy1), 1.0)

    return (overlap / inner_area) >= threshold


def _area(bbox: list[float]) -> float:
    x1, y1, x2, y2 = bbox
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


CONTAINER_TYPES: frozenset[str] = frozenset({
    "Card", "Panel", "Section", "Modal", "Toolbar", "AppBar", "TopBar",
    "Header", "Navbar", "Navigation", "Tab", "Tabs", "Container",
    "Screen", "Row", "Column", "Form", "Footer", "BottomNav", "BottomBar"
})


# ---------------------------------------------------------------------------
# Step 3 — Build hierarchy
# ---------------------------------------------------------------------------

def build_tree(components: list[dict]) -> list[dict]:
    """
    Assign each component as a child of the *smallest* container that
    contains it (80 % overlap).

    Leaf elements (Button, Input, Text, Link) can only be parents if their
    area is at least 2.5x larger than the child.

    Returns
    -------
    list[dict]
        Only top-level (root) components — children are nested inside them.
    """
    # Reset children
    for c in components:
        c["children"] = []

    n = len(components)
    assigned: set[int] = set()

    by_area = sorted(range(n), key=lambda i: _area(components[i]["bbox"]), reverse=True)

    for child_idx in range(n):
        child = components[child_idx]
        child_area = _area(child["bbox"])
        best_parent_idx: int | None = None
        best_area = float("inf")

        for parent_idx in by_area:
            if parent_idx == child_idx:
                continue
            parent = components[parent_idx]
            parent_area = _area(parent["bbox"])

            if parent_area <= child_area:
                continue

            # Protect leaf nodes from becoming parents unless significantly larger
            is_valid_container = (
                parent.get("type") in CONTAINER_TYPES or
                parent_area >= (2.5 * child_area)
            )
            if not is_valid_container:
                continue

            if inside(child["bbox"], parent["bbox"]):
                if parent_area < best_area:
                    best_area = parent_area
                    best_parent_idx = parent_idx

        if best_parent_idx is not None:
            components[best_parent_idx]["children"].append(child)
            assigned.add(child_idx)

    # Top-level roots = components that were not assigned to any parent
    roots = [components[i] for i in range(n) if i not in assigned]
    return roots


# ---------------------------------------------------------------------------
# Steps 4 & 5 — Row / column predicates
# ---------------------------------------------------------------------------

def same_row(a: dict, b: dict, min_overlap_ratio: float = 0.35) -> bool:
    """
    Return True when *a* and *b* share a visual row based on vertical overlap ratio.
    Resolution-independent and height-adaptive.
    """
    ay1, ay2 = a["bbox"][1], a["bbox"][3]
    by1, by2 = b["bbox"][1], b["bbox"][3]

    overlap_min = max(ay1, by1)
    overlap_max = min(ay2, by2)
    if overlap_max <= overlap_min:
        return False

    overlap_height = overlap_max - overlap_min
    min_height = min(ay2 - ay1, by2 - by1)

    if min_height <= 0:
        return False

    return (overlap_height / min_height) >= min_overlap_ratio


def same_column(a: dict, b: dict, tolerance: int = 25) -> bool:
    """
    Return True when *a* and *b* share similar X-centres (same visual column).
    """
    ax = (a["bbox"][0] + a["bbox"][2]) / 2
    bx = (b["bbox"][0] + b["bbox"][2]) / 2
    return abs(ax - bx) < tolerance


# ---------------------------------------------------------------------------
# Preprocessing Pass — Divider, Field, Input Icon, & Inline Action Merging
# ---------------------------------------------------------------------------

def detect_dividers(comps: list[dict]) -> list[dict]:
    """Identify 'or' / 'and' text separators and reclassify them as Divider nodes."""
    for c in comps:
        t = (c.get("text", "") or "").strip().lower()
        if t in ("or", "o r", "- or -", "-or-", "and"):
            c["type"] = "Divider"
            c["text"] = "or"
    return comps


def build_fields(comps: list[dict]) -> list[dict]:
    """
    Search for Text labels located directly above Input fields, and transform them
    into explicit Field component nodes containing label, input_type, and placeholder metadata.
    """
    inputs = [c for c in comps if c["type"].lower() == "input"]
    texts = [c for c in comps if c["type"].lower() == "text"]

    to_remove = set()
    for inp in inputs:
        ibox = inp["bbox"]
        best_label = None
        best_dist = float("inf")

        for txt in texts:
            if id(txt) in to_remove:
                continue
            tbox = txt["bbox"]
            v_dist = ibox[1] - tbox[3]
            if -10 <= v_dist <= 50:
                t_cx = (tbox[0] + tbox[2]) / 2
                if (ibox[0] - 30) <= t_cx <= (ibox[2] + 30):
                    if v_dist < best_dist:
                        best_dist = v_dist
                        best_label = txt

        display_text = inp.get("text", "").strip()
        label_text = best_label.get("text", "").strip() if best_label else (display_text if display_text else "")
        lower_combined = (label_text + " " + display_text).lower()

        input_type = "password" if "password" in lower_combined else ("email" if "email" in lower_combined else "text")
        placeholder = display_text if display_text else (f"Enter {label_text.lower()}" if label_text else "Enter text")

        inp["type"] = "Field"
        inp["label"] = label_text
        inp["input_type"] = input_type
        inp["placeholder"] = placeholder

        if best_label:
            to_remove.add(id(best_label))

    return [c for c in comps if id(c) not in to_remove]


def nest_input_icons(comps: list[dict]) -> list[dict]:
    """
    Nests Icon or Image components located inside an Input/Field bounding box
    directly inside Field.children.
    """
    fields = [c for c in comps if c.get("type", "").lower() in ("field", "input")]
    icons = [c for c in comps if c.get("type", "").lower() in ("icon", "image")]

    to_remove = set()
    for f in fields:
        fbox = f["bbox"]
        for icon in icons:
            if id(icon) in to_remove:
                continue
            ibox = icon["bbox"]
            # Check containment or trailing edge overlap inside field box
            if inside(ibox, fbox, threshold=0.50):
                f.setdefault("children", []).append(icon)
                to_remove.add(id(icon))

    return [c for c in comps if id(c) not in to_remove]


def merge_inline_text_actions(comps: list[dict]) -> list[dict]:
    """
    Search for co-linear / same-row Text and Link/Button elements
    (e.g., Text("Already have an account?") + Link("Log In")),
    and merge them into a single InlineAction component node.
    """
    texts = [c for c in comps if c.get("type", "").lower() == "text"]
    actions = [c for c in comps if c.get("type", "").lower() in ("link", "button")]

    to_remove = set()
    new_inlines = []

    for txt in texts:
        if id(txt) in to_remove:
            continue
        t_box = txt["bbox"]
        t_text = txt.get("text", "").strip()
        if not t_text:
            continue

        for act in actions:
            if id(act) in to_remove:
                continue
            a_box = act["bbox"]
            a_text = act.get("text", "").strip()

            # Check if they share a visual row
            if same_row(txt, act, min_overlap_ratio=0.30):
                # Ensure they are horizontally close (within 140px)
                gap = max(0, a_box[0] - t_box[2], t_box[0] - a_box[2])
                if gap <= 140:
                    combined_box = [
                        min(t_box[0], a_box[0]),
                        min(t_box[1], a_box[1]),
                        max(t_box[2], a_box[2]),
                        max(t_box[3], a_box[3]),
                    ]
                    # Order text first, action second
                    if t_box[0] <= a_box[0]:
                        prefix_text = t_text
                        link_text = a_text
                    else:
                        prefix_text = a_text
                        link_text = t_text

                    inline_node = {
                        "type": "InlineAction",
                        "bbox": combined_box,
                        "confidence": max(txt.get("confidence", 0.9), act.get("confidence", 0.9)),
                        "text": prefix_text,
                        "action_text": link_text,
                        "action_type": act.get("type", "Link"),
                        "text_confidence": 1.0,
                        "children": []
                    }
                    new_inlines.append(inline_node)
                    to_remove.add(id(txt))
                    to_remove.add(id(act))
                    break

    remaining = [c for c in comps if id(c) not in to_remove]
    return remaining + new_inlines


# ---------------------------------------------------------------------------
# Postprocessing Pass — Form & Card Clustering
# ---------------------------------------------------------------------------

def _wrap_if_form(group: list[dict]) -> list[dict]:
    """Wrap a sequence of contiguous form elements in a synthetic Card node."""
    if len(group) <= 1:
        return group

    has_input = any(c.get("type", "").lower() == "input" for c in group)
    has_button = any(c.get("type", "").lower() in ("button", "btn") for c in group)
    has_inline = any(c.get("type", "").lower() == "inlineaction" for c in group)

    if has_input or (has_button and len(group) >= 2) or has_inline:
        card = _make_synthetic("Card", group)
        card["is_form"] = True
        return [card]

    return group


STRUCTURAL_CONTAINERS: frozenset[str] = frozenset({
    "toolbar", "navbar", "navigation", "topbar", "header", "footer", "modal", "section", "appbar"
})


def group_form_cards(roots: list[dict]) -> list[dict]:
    """
    Cluster contiguous vertical form-like elements (inputs, labels, buttons, inline actions)
    into clean visual Card panels.
    """
    grouped_roots = []
    current_group = []

    for r in roots:
        r_type = r.get("type", "").lower()
        
        # Only explicit structural containers break form card groups
        is_structural = r_type in STRUCTURAL_CONTAINERS or (
            r.get("children") and r_type not in ("row", "column", "card", "button", "link", "text", "input", "inlineaction", "formgroup")
        )

        if not is_structural:
            current_group.append(r)
        else:
            if current_group:
                grouped_roots.extend(_wrap_if_form(current_group))
                current_group = []
            grouped_roots.append(r)

    if current_group:
        grouped_roots.extend(_wrap_if_form(current_group))

    return grouped_roots


# ---------------------------------------------------------------------------
# Step 6 — Group rows and columns
# ---------------------------------------------------------------------------

def _group_into_rows(items: list[dict], min_overlap_ratio: float = 0.35) -> list[list[dict]]:
    """
    Cluster *items* into horizontal rows using vertical overlap ratio.
    """
    rows: list[list[dict]] = []

    for item in sorted(items, key=lambda c: (c["bbox"][1] + c["bbox"][3]) / 2):
        placed = False
        for row in rows:
            if same_row(item, row[0], min_overlap_ratio):
                row.append(item)
                placed = True
                break
        if not placed:
            rows.append([item])

    # Sort each row left → right
    for row in rows:
        row.sort(key=lambda c: c["bbox"][0])

    return rows


def _make_synthetic(node_type: str, children: list[dict]) -> dict:
    """Create a synthetic layout node (Row / Column) wrapping *children*."""
    if not children:
        return {"type": node_type, "bbox": [0, 0, 0, 0], "confidence": 1.0,
                "text": "", "text_confidence": 0.0, "children": []}

    x1 = min(c["bbox"][0] for c in children)
    y1 = min(c["bbox"][1] for c in children)
    x2 = max(c["bbox"][2] for c in children)
    y2 = max(c["bbox"][3] for c in children)

    return {
        "type":             node_type,
        "bbox":             [x1, y1, x2, y2],
        "confidence":       1.0,
        "text":             "",
        "text_confidence":  0.0,
        "children":         children,
    }


def group_layout(
    roots: list[dict],
    row_tolerance: int = 25,
) -> list[dict]:
    """
    Wrap groups of roots into Row / Column synthetic nodes.

    Rules
    -----
    - Multiple components on the same visual row  → wrap in a ``Row`` node
    - Multiple components in a vertical stack      → wrap in a ``Column`` node
    - A single component that already has children → left as-is

    Applies recursively so nested containers are also grouped.
    """
    if not roots:
        return roots

    # Recurse into children first
    for root in roots:
        if root.get("children"):
            root["children"] = group_layout(root["children"], row_tolerance)

    # Cluster top-level roots into rows
    rows = _group_into_rows(roots, row_tolerance)

    result: list[dict] = []

    for row in rows:
        if len(row) == 1:
            result.append(row[0])
        else:
            result.append(_make_synthetic("Row", row))

    # Apply Card panel wrapping on vertical groupings
    result = group_form_cards(result)

    # If every entry in result is a single-column stack wrap them in a Column
    if len(result) > 1 and all(r["type"] != "Row" for r in result):
        return [_make_synthetic("Column", result)]

    return result


# ---------------------------------------------------------------------------
# Anchor type sets  (used by build_layout to pin top/bottom elements)
# ---------------------------------------------------------------------------

TOP_ANCHOR_TYPES: frozenset[str] = frozenset({
    "Toolbar", "AppBar", "TopBar", "StatusBar", "Header",
})

BOTTOM_ANCHOR_TYPES: frozenset[str] = frozenset({
    "BottomNavigation", "BottomNav", "TabBar", "BottomBar", "Footer",
})


def _quantize_margin(gap: int) -> str:
    """Map vertical gap in pixels to standard reusable CSS utility class."""
    if gap <= 10:
        return "mb-8"
    elif gap <= 14:
        return "mb-12"
    elif gap <= 18:
        return "mb-16"
    elif gap <= 22:
        return "mb-20"
    elif gap <= 28:
        return "mb-24"
    elif gap <= 34:
        return "mb-32"
    elif gap <= 38:
        return "mb-36"
    elif gap <= 44:
        return "mb-40"
    else:
        return "mb-48"


def compute_bounding_box_spacing(nodes: list[dict]) -> list[dict]:
    """
    Calculate vertical gaps between consecutive bounding boxes in a stack
    and attach quantized mb_class utility class to element metadata.
    """
    for node in nodes:
        children = node.get("children", [])
        if children:
            compute_bounding_box_spacing(children)

    # Compute gaps for vertical stack elements
    sorted_nodes = sorted(nodes, key=lambda n: n["bbox"][1])
    for i in range(len(sorted_nodes) - 1):
        curr = sorted_nodes[i]
        nxt = sorted_nodes[i + 1]

        c_box = curr.get("bbox", [0, 0, 0, 0])
        n_box = nxt.get("bbox", [0, 0, 0, 0])

        if c_box != [0, 0, 0, 0] and n_box != [0, 0, 0, 0]:
            v_gap = max(0, int(n_box[1] - c_box[3]))
            if 6 <= v_gap <= 65:
                curr["margin_bottom"] = v_gap
                curr["mb_class"] = _quantize_margin(v_gap)

    return nodes


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_layout(
    components: list[dict],
    row_tolerance: int = 25,
    img_height: int | None = None,
) -> list[dict]:
    """
    Full pipeline: detect_dividers → build_fields → nest_input_icons → inline_merge → sort → build_tree → group_layout → compute_spacing → reassemble.
    """
    comps = copy.deepcopy(components)

    # 1. Detect divider elements ("or", "and")
    comps = detect_dividers(comps)

    # 2. Build Field nodes (pair text labels + input fields)
    comps = build_fields(comps)

    # 3. Nest internal icons inside Field/Input nodes (e.g. eye toggle icons)
    comps = nest_input_icons(comps)

    # 4. Merge inline text + action pairs (e.g. "Already have an account?" + "Log In")
    comps = merge_inline_text_actions(comps)

    # 5. Sort top→bottom, left→right
    comps = sort_components(comps)

    # 6. Peel off anchored elements before hierarchy building
    def _is_top(c: dict) -> bool:
        if c["type"] not in TOP_ANCHOR_TYPES:
            return False
        if img_height:
            cy = (c["bbox"][1] + c["bbox"][3]) / 2
            return cy < img_height * 0.20
        return True

    def _is_bottom(c: dict) -> bool:
        if c["type"] not in BOTTOM_ANCHOR_TYPES:
            return False
        if img_height:
            cy = (c["bbox"][1] + c["bbox"][3]) / 2
            return cy > img_height * 0.80
        return True

    top_anchors    = [c for c in comps if _is_top(c)]
    bottom_anchors = [c for c in comps if _is_bottom(c)]
    free           = [c for c in comps if not _is_top(c) and not _is_bottom(c)]

    # 7. Build hierarchy + group for the free middle content
    free_roots = build_tree(free)
    free_tree  = group_layout(free_roots, row_tolerance)

    # 8. Reassemble: top | free | bottom
    result: list[dict] = []
    result.extend(sorted(top_anchors,    key=lambda c: c["bbox"][1]))
    result.extend(free_tree)
    result.extend(sorted(bottom_anchors, key=lambda c: c["bbox"][1]))

    # 9. Calculate dynamic bounding box spacing
    result = compute_bounding_box_spacing(result)

    return result
