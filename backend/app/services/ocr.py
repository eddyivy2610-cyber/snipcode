"""
services/ocr.py
===============
Re-exports the OCR primitives from app.ocr so the rest of the services
layer has a single canonical import path.
"""

from app.ocr import perform_ocr, get_ocr_reader, perform_full_ocr  # noqa: F401

__all__ = ["perform_ocr", "get_ocr_reader", "perform_full_ocr"]
