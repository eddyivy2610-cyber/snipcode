"""
renderers/icons.py
==================
Shared Icon Symbol Resolver for Snipcode Renderers.
"""

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

def resolve_icon(icon_name: str | None, default: str = "") -> str:
    """Resolve an icon string name to its symbol representation."""
    if not icon_name:
        return default
    return ICON_MAP.get(icon_name.lower(), default)
