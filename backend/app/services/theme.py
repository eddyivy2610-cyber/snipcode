"""
services/theme.py
=================
Design System & Theme Engine for Snipcode.
  - Manages Design Tokens (colors, typography, radii, shadows, spacing)
  - Provides Theme Presets (dark, light, cyber_blue)
  - Compiles Theme Tokens into CSS Custom Properties (:root variables)
  - Maps Semantic Design System Classes (card, btn-primary, input-standard) to tokens
  - Supports Tailwind Utility Class Export Mapping
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Theme:
    name: str
    bg_page: str
    bg_card: str
    bg_input: str
    border_card: str
    border_input: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent_primary: str
    accent_hover: str
    accent_gradient: str
    radius_card: str
    radius_input: str
    radius_btn: str
    shadow_card: str
    shadow_btn_hover: str
    font_family: str


DARK_THEME = Theme(
    name="dark",
    bg_page="#090d13",
    bg_card="#161b22",
    bg_input="#0d1117",
    border_card="#30363d",
    border_input="#30363d",
    text_primary="#f0f6fc",
    text_secondary="#c9d1d9",
    text_muted="#8b949e",
    accent_primary="#238636",
    accent_hover="#2ea44f",
    accent_gradient="linear-gradient(135deg, #238636, #2ea44f)",
    radius_card="16px",
    radius_input="8px",
    radius_btn="8px",
    shadow_card="0 16px 40px rgba(0, 0, 0, 0.45)",
    shadow_btn_hover="0 4px 14px rgba(46, 164, 79, 0.3)",
    font_family="'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
)

LIGHT_THEME = Theme(
    name="light",
    bg_page="#f6f8fa",
    bg_card="#ffffff",
    bg_input="#f3f4f6",
    border_card="#d0d7de",
    border_input="#d0d7de",
    text_primary="#1f2328",
    text_secondary="#24292f",
    text_muted="#57606a",
    accent_primary="#0969da",
    accent_hover="#1f883d",
    accent_gradient="linear-gradient(135deg, #0969da, #1f883d)",
    radius_card="16px",
    radius_input="8px",
    radius_btn="8px",
    shadow_card="0 10px 30px rgba(0, 0, 0, 0.08)",
    shadow_btn_hover="0 4px 14px rgba(9, 105, 218, 0.25)",
    font_family="'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
)

CYBER_BLUE_THEME = Theme(
    name="cyber_blue",
    bg_page="#030712",
    bg_card="#0f172a",
    bg_input="#1e293b",
    border_card="#334155",
    border_input="#334155",
    text_primary="#f8fafc",
    text_secondary="#e2e8f0",
    text_muted="#94a3b8",
    accent_primary="#2563eb",
    accent_hover="#3b82f6",
    accent_gradient="linear-gradient(135deg, #1d4ed8, #3b82f6)",
    radius_card="20px",
    radius_input="10px",
    radius_btn="10px",
    shadow_card="0 20px 50px rgba(37, 99, 235, 0.25)",
    shadow_btn_hover="0 4px 20px rgba(59, 130, 246, 0.4)",
    font_family="'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"
)


class ThemeRegistry:
    """Registry managing themes and CSS Custom Property generation."""

    _themes: dict[str, Theme] = {
        "dark": DARK_THEME,
        "light": LIGHT_THEME,
        "cyber_blue": CYBER_BLUE_THEME,
        "blue": CYBER_BLUE_THEME,
    }

    @classmethod
    def register_theme(cls, name: str, theme: Theme) -> None:
        """Register a new theme at runtime."""
        cls._themes[name.lower()] = theme

    @classmethod
    def get_theme(cls, name: str = "dark") -> Theme:
        """Retrieve theme preset by name, defaulting to DARK_THEME."""
        return cls._themes.get((name or "dark").lower(), DARK_THEME)

    @classmethod
    def get_theme_css(cls, theme_name: str = "dark") -> str:
        """Generate full CSS stylesheet rules using CSS Custom Properties."""
        t = cls.get_theme(theme_name)

        css_lines = [
            "/* Snipcode Design System Theme Stylesheet */",
            "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');",
            "",
            ":root {",
            f"  --bg-page: {t.bg_page};",
            f"  --bg-card: {t.bg_card};",
            f"  --bg-input: {t.bg_input};",
            f"  --border-card: {t.border_card};",
            f"  --border-input: {t.border_input};",
            f"  --text-primary: {t.text_primary};",
            f"  --text-secondary: {t.text_secondary};",
            f"  --text-muted: {t.text_muted};",
            f"  --accent-primary: {t.accent_primary};",
            f"  --accent-hover: {t.accent_hover};",
            f"  --accent-gradient: {t.accent_gradient};",
            f"  --radius-card: {t.radius_card};",
            f"  --radius-input: {t.radius_input};",
            f"  --radius-btn: {t.radius_btn};",
            f"  --shadow-card: {t.shadow_card};",
            f"  --shadow-btn-hover: {t.shadow_btn_hover};",
            f"  --font-family: {t.font_family};",
            "}",
            "",
            "* { box-sizing: border-box; margin: 0; padding: 0; }",
            "",
            "body {",
            "  font-family: var(--font-family);",
            "  background: var(--bg-page);",
            "  color: var(--text-secondary);",
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
            "  background: var(--bg-card);",
            "  border: 1px solid var(--border-card);",
            "  border-radius: var(--radius-card);",
            "  padding: 36px 32px;",
            "  box-shadow: var(--shadow-card);",
            "  display: flex;",
            "  flex-direction: column;",
            "  gap: 20px;",
            "}",
            "",
            "/* --- Semantic Design System Components --- */",
            ".card, .form-card {",
            "  background: var(--bg-card);",
            "  border: 1px solid var(--border-card);",
            "  border-radius: var(--radius-card);",
            "  padding: 28px 24px;",
            "  display: flex;",
            "  flex-direction: column;",
            "  gap: 18px;",
            "  width: 100%;",
            "  box-shadow: var(--shadow-card);",
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
            "  color: var(--text-muted);",
            "}",
            "",
            ".form-input {",
            "  padding: 12px 16px;",
            "  background: var(--bg-input);",
            "  border: 1px solid var(--border-input);",
            "  border-radius: var(--radius-input);",
            "  color: var(--text-primary);",
            "  font-size: 0.95rem;",
            "  width: 100%;",
            "  transition: border-color 0.2s, box-shadow 0.2s;",
            "}",
            ".form-input:focus { outline: none; border-color: var(--accent-hover); box-shadow: 0 0 0 3px rgba(88,166,255,0.15); }",
            "",
            ".btn {",
            "  padding: 12px 24px;",
            "  border-radius: var(--radius-btn);",
            "  font-weight: 600;",
            "  font-size: 0.95rem;",
            "  cursor: pointer;",
            "  border: none;",
            "  transition: all 0.2s ease;",
            "  background: var(--accent-gradient);",
            "  color: white;",
            "  display: inline-flex;",
            "  align-items: center;",
            "  justify-content: center;",
            "  width: 100%;",
            "  gap: 8px;",
            "}",
            ".btn:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: var(--shadow-btn-hover); }",
            "",
            ".nav-link { color: #58a6ff; text-decoration: none; font-weight: 600; transition: color 0.2s; }",
            ".nav-link:hover { color: #79c0ff; text-decoration: underline; }",
            "",
            ".inline-action {",
            "  font-size: 0.9rem;",
            "  color: var(--text-muted);",
            "  text-align: center;",
            "  margin-top: 8px;",
            "}",
            "",
            ".text-content { font-size: 1rem; line-height: 1.6; color: var(--text-primary); }",
            ".container-title { font-size: 1.35rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; text-align: center; }",
            "",
            ".divider {",
            "  display: flex;",
            "  align-items: center;",
            "  text-align: center;",
            "  color: var(--text-muted);",
            "  font-size: 0.85rem;",
            "  font-weight: 600;",
            "  margin: 12px 0;",
            "  width: 100%;",
            "}",
            ".divider::before, .divider::after {",
            "  content: '';",
            "  flex: 1;",
            "  border-bottom: 1px solid var(--border-card);",
            "}",
            ".divider span { padding: 0 12px; text-transform: uppercase; letter-spacing: 0.05em; }",
            "",
            ".input-wrapper { position: relative; display: flex; align-items: center; width: 100%; }",
            ".input-icon { position: absolute; right: 14px; cursor: pointer; font-size: 1.1rem; color: var(--text-muted); user-select: none; }",
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
        return "\n".join(css_lines)


def map_to_tailwind(comp_class: str) -> str:
    """Map semantic design system class to Tailwind CSS utility classes."""
    tailwind_map = {
        "card": "bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col gap-4 w-full",
        "form-card": "bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col gap-4 w-full",
        "form-group": "flex flex-col gap-1.5 w-full text-left",
        "form-label": "text-sm font-semibold text-slate-400",
        "form-input": "py-3 px-4 bg-slate-950 border border-slate-800 rounded-lg text-white w-full focus:outline-none focus:border-blue-500",
        "btn": "py-3 px-6 rounded-lg font-semibold bg-emerald-600 hover:bg-emerald-500 text-white w-full flex items-center justify-center gap-2 transition-all",
        "divider": "flex items-center text-center text-slate-400 text-xs font-semibold my-3 w-full",
        "inline-action": "text-sm text-slate-400 text-center mt-2",
        "container-title": "text-xl font-bold text-white text-center mb-2",
    }
    return tailwind_map.get(comp_class, comp_class)
