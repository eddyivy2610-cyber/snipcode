"""
services/semantic_ir.py
========================
4-Pillar Design-System Intermediate Representation (IR v4.0) Compiler Engine:
  Translates hierarchical layout tree nodes into an industry-grade 4-pillar IR architecture.

  Decouples every UI component into four explicit pillars + metadata:
    - id: Unique, descriptive component identifier
    - type: UI Component primitive ("Form", "Input", "Button", "Divider", "InlineAction")
    - variant: Design system style variant ("primary", "secondary", "oauth", "divider", "inline")
    - content: Pure UI text & content (title, label, placeholder, text, icon)
    - layout: Framework-neutral spatial metrics (width, margin_bottom, alignment)
    - style: Visual & theme styling properties (corner_radius, elevation, theme)
    - behavior: Interactive action handlers (action: "submit_google", "navigate_login")
    - children: Nested component hierarchy array
"""

from __future__ import annotations
import re
from typing import Dict, List, Any, Optional


def _slugify(text: str) -> str:
    """Convert text label into clean identifier slug."""
    clean = re.sub(r'[^a-zA-Z0-9]', '_', text.strip().lower())
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean if clean else "item"


def build_semantic_ir(layout_tree: list[dict]) -> dict[str, Any]:
    """
    Compile a Component Layout Tree into a 4-Pillar Design-System IR v4.0 dictionary.
    """
    ir_components = []

    for root in layout_tree:
        node_type = root.get("type", "").lower()

        if node_type in ("card", "form", "screen") or root.get("is_form"):
            form_ir = _parse_form_node(root)
            ir_components.append(form_ir)
        else:
            ir_components.append(_parse_generic_node(root))

    return {
        "schema_version": "4.0",
        "components": ir_components
    }


def _infer_icon_name(text: str, comp_type: str, children: list[dict]) -> Optional[str]:
    """Infer explicit named icon string from component text, type, or children."""
    lower_t = text.lower()
    if "eye" in lower_t or "visibility" in lower_t or "password" in lower_t:
        return "eye"
    elif "search" in lower_t:
        return "search"
    elif "mail" in lower_t or "email" in lower_t:
        return "mail"
    elif "lock" in lower_t:
        return "lock"
    elif "user" in lower_t or "profile" in lower_t:
        return "user"
    elif "calendar" in lower_t or "date" in lower_t:
        return "calendar"

    for child in children:
        c_text = (child.get("text", "") or "").lower()
        if "eye" in c_text or "see" in c_text:
            return "eye"
        elif child.get("type", "").lower() in ("icon", "image"):
            return "eye"

    return None


def _parse_form_node(node: dict) -> dict[str, Any]:
    """Compile container node into a 4-Pillar Form IR node with nested children."""
    raw_children = node.get("children", [])
    title = (node.get("text", "") or "").strip()

    form_children = []

    for child in raw_children:
        c_type = child.get("type", "").lower()
        c_text = (child.get("text", "") or "").strip()
        v_gap = child.get("margin_bottom")

        # Layout pillar
        layout_pillar = {"width": "fill"}
        if v_gap:
            layout_pillar["margin_bottom"] = v_gap

        # Style pillar
        style_pillar = {
            "corner_radius": "medium",
            "elevation": "low"
        }

        if c_type in ("field", "input"):
            label = child.get("label", "") or (c_text if c_text and c_text.lower() not in ("email", "password", "input") else "")
            lower_comb = (label + " " + c_text).lower()
            input_type = child.get("input_type") or ("password" if "password" in lower_comb else ("email" if "email" in lower_comb else "text"))
            placeholder = child.get("placeholder") or (c_text if c_text else f"Enter {label.lower() if label else 'text'}")

            child_icons = child.get("children", [])
            trailing_icon = _infer_icon_name(c_text, c_type, child_icons)
            if input_type == "password" and not trailing_icon:
                trailing_icon = "eye"

            field_id = f"field_{_slugify(label if label else input_type)}"

            content_pillar = {
                "label": label,
                "placeholder": placeholder
            }
            if trailing_icon:
                content_pillar["icon"] = trailing_icon

            behavior_pillar = {
                "action": f"input_{_slugify(label if label else input_type)}"
            }

            field_node = {
                "id": field_id,
                "type": "Input",
                "input_type": input_type,
                "variant": "standard",
                "content": content_pillar,
                "layout": layout_pillar,
                "style": style_pillar,
                "behavior": behavior_pillar
            }
            form_children.append(field_node)

        elif c_type == "divider":
            divider_id = f"divider_{_slugify(c_text if c_text else 'or')}"
            form_children.append({
                "id": divider_id,
                "type": "Divider",
                "variant": "divider",
                "content": {
                    "text": c_text if c_text else "or"
                },
                "layout": layout_pillar,
                "style": {
                    "border_style": "solid",
                    "opacity": 0.6
                },
                "behavior": {}
            })

        elif c_type == "inlineaction" or "already have an account" in c_text.lower():
            inline_id = "action_login_inline"
            form_children.append({
                "id": inline_id,
                "type": "InlineAction",
                "variant": "inline",
                "content": {
                    "text": "Already have an account?",
                    "link_text": "Log In"
                },
                "layout": layout_pillar,
                "style": {
                    "text_align": "center"
                },
                "behavior": {
                    "action": "navigate_login"
                }
            })

        elif c_type == "button":
            lower_text = c_text.lower()
            variant = "primary"
            provider = None
            icon = None

            if "google" in lower_text:
                variant = "oauth"
                provider = "Google"
                icon = "google"
            elif "apple" in lower_text:
                variant = "oauth"
                provider = "Apple"
                icon = "apple"
            elif "github" in lower_text:
                variant = "oauth"
                provider = "GitHub"
                icon = "github"

            btn_id = f"btn_{_slugify(provider.lower() if provider else c_text)}"

            content_pillar = {
                "text": c_text if c_text else "Submit"
            }
            if icon:
                content_pillar["icon"] = icon

            behavior_action = f"submit_{provider.lower()}" if provider else "submit_form"

            btn_node = {
                "id": btn_id,
                "type": "Button",
                "variant": variant,
                "content": content_pillar,
                "layout": layout_pillar,
                "style": style_pillar,
                "behavior": {
                    "action": behavior_action
                }
            }
            form_children.append(btn_node)

        elif c_type == "text" and not title and ("sign" in c_text.lower() or "create" in c_text.lower() or "login" in c_text.lower()):
            title = c_text

    form_id = f"form_{_slugify(title if title else 'signup')}"

    return {
        "id": form_id,
        "type": "Form",
        "variant": "card",
        "content": {
            "title": title if title else "Sign Up"
        },
        "layout": {
            "width": 420,
            "alignment": "center"
        },
        "style": {
            "corner_radius": "large",
            "elevation": "medium",
            "theme": "dark"
        },
        "behavior": {
            "action": "submit_form"
        },
        "children": form_children
    }


def _parse_generic_node(node: dict) -> dict[str, Any]:
    """Parse generic non-form component into 4-pillar IR v4.0 dictionary."""
    n_type = node.get("type", "Component")
    text = node.get("text", "")
    children = node.get("children", [])
    v_gap = node.get("margin_bottom")

    item_id = f"{_slugify(n_type)}_{_slugify(text)}"

    parsed = {
        "id": item_id,
        "type": n_type,
        "variant": "default",
        "content": {
            "text": text
        },
        "layout": {},
        "style": {},
        "behavior": {}
    }
    if v_gap:
        parsed["layout"]["margin_bottom"] = v_gap
    if children:
        parsed["children"] = [_parse_generic_node(c) for c in children]

    return parsed
