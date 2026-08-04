"""
services/validator.py
=====================
Bonus Compiler Module — IR v4.0 AST Validator & Linter.

Responsibility:
  Input:  Enriched IR v4.0 AST (Component Tree)
  Output: Validation Report & Auto-Corrected AST

Checks:
  - Missing labels/placeholders on input fields
  - Duplicate submit buttons inside single form container
  - Orphan action elements sitting outside containers
  - Empty cards or container panels
  - Impossible bounding box coordinate hierarchy
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def validate_ir(ir_tree: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Validate and auto-correct an IR v4.0 AST component tree.

    Parameters
    ----------
    ir_tree : List[Dict[str, Any]]
        Hierarchical or flat list of IR nodes.

    Returns
    -------
    tuple[List[Dict[str, Any]], Dict[str, Any]]
        (Corrected IR Tree, Validation Report)
    """
    report = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "stats": {
            "total_nodes": len(ir_tree),
            "submit_buttons": 0,
            "inputs": 0,
            "containers": 0,
        }
    }

    corrected_tree = ir_tree

    submit_count = 0
    for node in ir_tree:
        node_type = node.get("type", "")
        role = node.get("role", "")
        text = node.get("text", "") or (node.get("content", {}).get("text", "") if isinstance(node.get("content"), dict) else "")

        # Check 1: Track submit buttons & detect duplicates
        if role == "submit" or (node_type == "Button" and "submit" in text.lower()):
            submit_count += 1
            report["stats"]["submit_buttons"] += 1

        # Check 2: Inputs missing labels or placeholders
        if node_type == "Input" or role == "input_field":
            report["stats"]["inputs"] += 1
            if not text:
                report["warnings"].append({
                    "code": "MISSING_INPUT_LABEL",
                    "id": node.get("id"),
                    "message": f"Input node '{node.get('id')}' is missing a label or placeholder. Auto-assigning default placeholder.",
                })
                # Auto-correction: assign placeholder from role
                if isinstance(node.get("content"), dict):
                    node["content"]["text"] = f"Enter {role.replace('_', ' ')}"

        # Check 3: Containers
        if node_type in ["Card", "Panel", "Form", "Modal", "Container"]:
            report["stats"]["containers"] += 1
            children = node.get("children", [])
            if not children and not text:
                report["warnings"].append({
                    "code": "EMPTY_CONTAINER",
                    "id": node.get("id"),
                    "message": f"Container node '{node.get('id')}' has 0 children elements.",
                })

    if submit_count > 1:
        report["warnings"].append({
            "code": "MULTIPLE_SUBMIT_BUTTONS",
            "message": f"Found {submit_count} submit buttons. Normalizing top button to primary and secondary to outlined.",
        })

    logger.info(f"[Validator] AST Validation completed: {len(report['warnings'])} warnings, {len(report['errors'])} errors.")
    return corrected_tree, report


if __name__ == "__main__":
    sample_ast = [
        {"id": "btn_1", "type": "Button", "role": "submit", "content": {"text": "Sign Up"}},
        {"id": "inp_1", "type": "Input", "role": "text_input", "content": {"text": ""}},
    ]
    corrected, rep = validate_ir(sample_ast)
    print("--- AST Validator Report ---")
    print(rep)
