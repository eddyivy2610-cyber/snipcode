"""
inference.py — compatibility shim
==================================
The detection logic now lives in app/services/detector.py.
This module re-exports `detect` so any existing code that imports
`from app.inference import detect` continues to work unchanged.
"""

from app.services.detector import detect  # noqa: F401

__all__ = ["detect"]