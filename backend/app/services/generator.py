"""
services/generator.py
=====================
Converts the structured Component tree from services/layout.py into
HTML + CSS output.

Works with plain dicts (the layout engine's output format) rather than
LayoutNode objects, making it easier to test and serialise.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# CSS baseline — written once into every generated page
# ---------------------------------------------------------------------------

_BASE_CSS: list[str] = [
    "/* Snipcode Generated Stylesheet */",
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');",
    "",
    "* { box-sizing: border-box; margin: 0; padding: 0; }",
    "",
    "body {",
    "  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;",
    "  background: #090d13;",
    "  color: #c9d1d9;",
    "  padding: 40px 20px;",
    "  display: flex;",
    "  flex-direction: column;",
    "  align-items: center;",
    "  justify-content: center;",
    "  min-height: 100vh;",
    "}",
    "",
    ".screen {",
    "  width: 100%;",
    "  max-width: 480px;",
    "  margin: 0 auto;",
    "  background: #161b22;",
    "  border: 1px solid #30363d;",
    "  border-radius: 16px;",
    "  padding: 36px 32px;",
    "  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);",
    "  display: flex;",
    "  flex-direction: column;",
    "  gap: 20px;",
    "}",
    "",
    "/* --- Layout containers --- */",
    ".layout-row {",
    "  display: flex;",
    "  flex-direction: row;",
    "  flex-wrap: wrap;",
    "  gap: 16px;",
    "  align-items: center;",
    "  width: 100%;",
    "}",
    "",
    ".layout-column {",
    "  display: flex;",
    "  flex-direction: column;",
    "  gap: 18px;",
    "  width: 100%;",
    "}",
    "",
    "/* --- Form & Card Container --- */",
    ".card, .form-card {",
    "  background: #161b22;",
    "  border: 1px solid #30363d;",
    "  border-radius: 16px;",
    "  padding: 28px 24px;",
    "  display: flex;",
    "  flex-direction: column;",
    "  gap: 18px;",
    "  width: 100%;",
    "  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);",
    "}",
    "",
    ".form-group {",
    "  display: flex;",
    "  flex-direction: column;",
    "  gap: 6px;",
    "  width: 100%;",
    "  text-align: left;",
    "}",
    "",
    ".form-label {",
    "  font-size: 0.875rem;",
    "  font-weight: 600;",
    "  color: #8b949e;",
    "}",
    "",
    ".form-input {",
    "  padding: 12px 16px;",
    "  background: #0d1117;",
    "  border: 1px solid #30363d;",
    "  border-radius: 8px;",
    "  color: #f0f6fc;",
    "  font-size: 0.95rem;",
    "  width: 100%;",
    "  transition: border-color 0.2s, box-shadow 0.2s;",
    "}",
    ".form-input:focus { outline: none; border-color: #58a6ff; box-shadow: 0 0 0 3px rgba(88,166,255,0.15); }",
    "",
    "/* --- Action Buttons & Links --- */",
    ".btn {",
    "  padding: 12px 24px;",
    "  border-radius: 8px;",
    "  font-weight: 600;",
    "  font-size: 0.95rem;",
    "  cursor: pointer;",
    "  border: none;",
    "  transition: all 0.2s ease;",
    "  background: linear-gradient(135deg, #238636, #2ea44f);",
    "  color: white;",
    "  display: inline-flex;",
    "  align-items: center;",
    "  justify-content: center;",
    "  width: 100%;",
    "  gap: 8px;",
    "}",
    ".btn:hover { background: #2ea44f; transform: translateY(-1px); box-shadow: 0 4px 14px rgba(46,164,79,0.3); }",
    "",
    ".nav-link { color: #58a6ff; text-decoration: none; font-weight: 600; transition: color 0.2s; }",
    ".nav-link:hover { color: #79c0ff; text-decoration: underline; }",
    "",
    ".inline-action {",
    "  font-size: 0.9rem;",
    "  color: #8b949e;",
    "  text-align: center;",
    "  margin-top: 8px;",
    "}",
    "",
    ".text-content { font-size: 1rem; line-height: 1.6; color: #e6edf3; }",
    ".container-title { font-size: 1.35rem; font-weight: 700; color: #f0f6fc; margin-bottom: 8px; text-align: center; }",
    "",
    "/* --- Dividers --- */",
    ".divider {",
    "  display: flex;",
    "  align-items: center;",
    "  text-align: center;",
    "  color: #8b949e;",
    "  font-size: 0.85rem;",
    "  font-weight: 600;",
    "  margin: 12px 0;",
    "  width: 100%;",
    "}",
    ".divider::before, .divider::after {",
    "  content: '';",
    "  flex: 1;",
    "  border-bottom: 1px solid #30363d;",
    "}",
    ".divider span { padding: 0 12px; text-transform: uppercase; letter-spacing: 0.05em; }",
    "",
    "/* --- Input Wrappers & Icons --- */",
    ".input-wrapper {",
    "  position: relative;",
    "  display: flex;",
    "  align-items: center;",
    "  width: 100%;",
    "}",
    ".input-icon {",
    "  position: absolute;",
    "  right: 14px;",
    "  cursor: pointer;",
    "  font-size: 1.1rem;",
    "  color: #8b949e;",
    "  user-select: none;",
    "}",
    ".btn-icon { font-size: 1.1rem; display: inline-flex; align-items: center; margin-right: 6px; }",
    "",
    "/* --- Reusable Spacing Utility Classes --- */",
    ".mb-8  { margin-bottom: 8px !important; }",
    ".mb-12 { margin-bottom: 12px !important; }",
    ".mb-16 { margin-bottom: 16px !important; }",
    ".mb-20 { margin-bottom: 20px !important; }",
    ".mb-24 { margin-bottom: 24px !important; }",
    ".mb-32 { margin-bottom: 32px !important; }",
    ".mb-36 { margin-bottom: 36px !important; }",
    ".mb-40 { margin-bottom: 40px !important; }",
    ".mb-48 { margin-bottom: 48px !important; }",
]

# ---------------------------------------------------------------------------
# Container type → HTML tag + CSS class
# ---------------------------------------------------------------------------

_CONTAINER_MAP: dict[str, tuple[str, str]] = {
    # type_lower       : (html_tag,   css_class)
    "toolbar":           ("header",   "toolbar"),
    "appbar":            ("header",   "appbar"),
    "topbar":            ("header",   "topbar"),
    "header":            ("header",   "header"),
    "navigation":        ("nav",      "navbar"),
    "modal":             ("div",      "modal"),
    "card":              ("form",     "card form-card"),
    "panel":             ("div",      "panel"),
    "section":           ("section",  "section"),
    "tab":               ("div",      "tabs-container"),
    "bottomnavigation":  ("nav",      "bottom-nav"),
    "bottomnav":         ("nav",      "bottom-nav"),
    "tabbar":            ("nav",      "bottom-nav"),
    "bottombar":         ("nav",      "bottom-nav"),
    "footer":            ("footer",   "footer"),
    # Synthetic nodes from the layout engine
    "row":               ("div",      "layout-row"),
    "column":            ("div",      "layout-column"),
    "screen":            ("main",     "screen"),
}


def _cls(base_cls: str, mb_cls: str) -> str:
    """Helper to join base CSS class with optional margin utility class."""
    return f"{base_cls} {mb_cls}".strip() if mb_cls else base_cls


def _render_node(node: dict, indent: int, parts: list[str]) -> None:
    """Recursively render a Component dict to HTML lines appended to *parts*."""
    sp = "  " * indent
    node_type = node.get("type", "div")
    node_type_lower = node_type.lower()
    children = node.get("children", [])
    text = (node.get("text", "") or "").strip()
    label = (node.get("label", "") or "").strip()
    mb_cls = node.get("mb_class", "")

    # ----- Container / synthetic node -----
    if (children and node_type_lower not in ("field", "input", "button")) or node_type_lower in _CONTAINER_MAP:
        tag, css = _CONTAINER_MAP.get(node_type_lower, ("div", node_type_lower))
        parts.append(f"{sp}<{tag} class=\"{_cls(css, mb_cls)}\">")

        # Emit container text title if present
        if text and text.lower() != node_type_lower and node_type_lower not in ("row", "column", "screen"):
            parts.append(f"{sp}  <h2 class=\"container-title mb-24\">{text}</h2>")

        for child in children:
            _render_node(child, indent + 1, parts)
        parts.append(f"{sp}</{tag}>")
        return

    # ----- Leaf elements & Field abstractions -----
    display_text = text if text else node_type

    if node_type_lower == "field":
        input_type = node.get("input_type", "text")
        placeholder = node.get("placeholder", "Enter text")
        icon_html = ""
        if children or input_type == "password":
            icon_html = ' <span class="input-icon">👁️</span>'

        parts.append(f"{sp}<div class=\"{_cls('form-group', mb_cls)}\">")
        if label:
            parts.append(f"{sp}  <label class=\"form-label\">{label}</label>")
        parts.append(f"{sp}  <div class=\"input-wrapper\">")
        parts.append(f"{sp}    <input type=\"{input_type}\" class=\"form-input\" placeholder=\"{placeholder}\" />{icon_html}")
        parts.append(f"{sp}  </div>")
        parts.append(f"{sp}</div>")

    elif node_type_lower == "divider":
        parts.append(f"{sp}<div class=\"{_cls('divider', mb_cls)}\"><span>{display_text}</span></div>")

    elif node_type_lower == "inlineaction" or "already have an account" in display_text.lower():
        if "already have an account" in display_text.lower():
            prefix_text = "Already have an account?"
            action_text = "Log In"
        else:
            prefix_text = display_text
            action_text = node.get("action_text", "Click here")
        parts.append(f"{sp}<p class=\"{_cls('inline-action', mb_cls)}\">{prefix_text} <a href=\"#\" class=\"nav-link\">{action_text}</a></p>")

    elif node_type_lower == "button":
        brand_icon = ""
        lower_t = display_text.lower()
        if "google" in lower_t:
            brand_icon = '<span class="btn-icon">🌐</span> '
        elif "apple" in lower_t:
            brand_icon = '<span class="btn-icon">🍎</span> '
        elif "github" in lower_t:
            brand_icon = '<span class="btn-icon">🐙</span> '
        elif children:
            brand_icon = '<span class="btn-icon">✨</span> '
        parts.append(f"{sp}<button class=\"{_cls('btn', mb_cls)}\">{brand_icon}{display_text}</button>")

    elif node_type_lower == "text":
        parts.append(f"{sp}<p class=\"{_cls('text-content', mb_cls)}\">{display_text}</p>")

    elif node_type_lower == "input":
        lower_t = (display_text + " " + label).lower()
        input_type = "password" if "password" in lower_t else ("email" if "email" in lower_t else "text")
        icon_html = ' <span class="input-icon">👁️</span>' if input_type == "password" else ""

        if label:
            parts.append(f"{sp}<div class=\"{_cls('form-group', mb_cls)}\">")
            parts.append(f"{sp}  <label class=\"form-label\">{label}</label>")
            parts.append(f"{sp}  <div class=\"input-wrapper\">")
            parts.append(f"{sp}    <input type=\"{input_type}\" class=\"form-input\" placeholder=\"Enter {label.lower()}\" />{icon_html}")
            parts.append(f"{sp}  </div>")
            parts.append(f"{sp}</div>")
        else:
            parts.append(f"{sp}<div class=\"{_cls('input-wrapper', mb_cls)}\">")
            parts.append(f"{sp}  <input type=\"{input_type}\" class=\"form-input\" placeholder=\"{display_text}\" />{icon_html}")
            parts.append(f"{sp}</div>")
    elif node_type_lower == "image":
        parts.append(f"{sp}<div class=\"{_cls('image-placeholder', mb_cls)}\">🖼️ {display_text}</div>")
    elif node_type_lower == "icon":
        parts.append(f"{sp}<span class=\"{_cls('icon-element', mb_cls)}\">✨ {display_text}</span>")
    elif node_type_lower == "link":
        parts.append(f"{sp}<a href=\"#\" class=\"{_cls('nav-link', mb_cls)}\">{display_text}</a>")
    elif node_type_lower == "checkbox":
        parts.append(f"{sp}<label class=\"{_cls('checkbox-container', mb_cls)}\"><input type=\"checkbox\" /> {display_text}</label>")
    elif node_type_lower == "toggle":
        parts.append(f"{sp}<label class=\"{_cls('toggle-container', mb_cls)}\"><input type=\"checkbox\" class=\"toggle-input\" /> {display_text}</label>")
    elif node_type_lower in ("tab",):
        parts.append(f"{sp}<div class=\"{_cls('tab-item', mb_cls)}\">{display_text}</div>")
    else:
        parts.append(f"{sp}<div class=\"{_cls(node_type_lower, mb_cls)}\">{display_text}</div>")


def generate(tree: list[dict]) -> tuple[str, str]:
    """
    Convert a Component tree into HTML + CSS via the 4-Pillar IR v4.0 Compiler & Renderer Registry.
    """
    from app.services.semantic_ir import build_semantic_ir
    ir = build_semantic_ir(tree)
    return generate_from_ir(ir)

    full_html = (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "  <title>Snipcode Live Preview</title>\n"
        "  <style>\n"
        + "\n".join(f"    {line}" for line in _BASE_CSS)
        + "\n  </style>\n"
        "</head>\n"
        "<body>\n"
        f"{html_body}\n"
        "</body>\n"
        "</html>"
    )

    css = "\n".join(_BASE_CSS)
    return full_html, css


ICON_MAP = {
    "eye": "👁️",
    "visibility": "👁️",
    "mail": "✉️",
    "email": "✉️",
    "lock": "🔒",
    "search": "🔍",
    "user": "👤",
    "calendar": "📅",
    "google": "🌐",
    "apple": "🍎",
    "github": "🐙",
}


def _spacing_to_mb_class(spacing: int | None) -> str:
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


from app.services.renderers.registry import RendererRegistry
from app.services.renderers.base import RenderContext


def generate_from_ir(ir: dict, ctx: RenderContext | None = None) -> tuple[str, str]:
    """
    Render clean HTML and CSS directly from a Design-System IR v4.0 structure
    using the Component Renderer Registry strategy pattern.
    """
    if ctx is None:
        ctx = RenderContext()

    html_parts: list[str] = ['<main class="screen">']

from app.services.theme import ThemeRegistry
from app.services.vnode import build_vnode_tree, HTMLSerializer


def generate_from_ir(ir: dict, ctx: RenderContext | None = None) -> tuple[str, str]:
    """
    Render clean HTML and CSS directly from a Design-System IR v4.0 structure
    using Virtual UI Tree (VNode AST) compilation and Theme Engine.
    """
    if ctx is None:
        ctx = RenderContext()

    vnode_roots = build_vnode_tree(ir)

    html_parts: list[str] = ['<main class="screen">']
    for root_vnode in vnode_roots:
        html_parts.append(HTMLSerializer.serialize(root_vnode, indent=1))

    html_parts.append('</main>')
    html_body = "\n".join(html_parts)

    css = ThemeRegistry.get_theme_css(ctx.theme)

    full_html = (
        "<!DOCTYPE html>\n"
        f"<html lang=\"en\" data-theme=\"{ctx.theme}\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "  <title>Snipcode Live Preview</title>\n"
        "  <style>\n"
        f"{css}\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        f"{html_body}\n"
        "</body>\n"
        "</html>"
    )

    return full_html, css
