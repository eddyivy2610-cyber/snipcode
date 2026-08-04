"""
agent/memory.py
===============
Agent Memory & AST Mutation Engine.

Maintains state:
  - current_ast: The single source of truth IR v5.0 AST
  - original_image_path: Path to original uploaded screenshot
  - generated_code: Active compiled target code (HTML/React)
  - similarity_score: SSIM visual score against original image
  - history: Log of AST repairs and user mutations

Provides deterministic AST mutation methods without re-running vision detectors.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    State container for a single compiler session.
    """

    def __init__(self, session_id: str = "default_session"):
        self.session_id: str = session_id
        self.original_image_path: Optional[str] = None
        self.current_ast: List[Dict[str, Any]] = []
        self.generated_code: Dict[str, str] = {"html": "", "css": ""}
        self.similarity_score: float = 0.0
        self.history: List[Dict[str, Any]] = []

    def set_ast(self, ast: List[Dict[str, Any]], source: str = "fusion"):
        """Update active AST state."""
        self.current_ast = copy.deepcopy(ast)
        self.history.append({
            "action": "set_ast",
            "source": source,
            "total_nodes": len(ast),
        })
        logger.info(f"[AgentMemory] AST updated ({len(ast)} root nodes) from '{source}'.")

    def get_ast(self) -> List[Dict[str, Any]]:
        """Retrieve active AST."""
        return self.current_ast

    def mutate_node(self, node_id: str, field_updates: Dict[str, Any]) -> bool:
        """
        Mutate a specific AST node in-place by ID.

        Parameters
        ----------
        node_id : str
            Target node identifier (e.g. 'btn_sign_up').
        field_updates : Dict[str, Any]
            Fields to update (e.g. {'variant': 'secondary', 'content': {'text': 'Submit Now'}}).

        Returns
        -------
        bool
            True if node was found and updated.
        """
        target = self._find_node_by_id(self.current_ast, node_id)
        if not target:
            logger.warning(f"[AgentMemory] Mutation failed: Node ID '{node_id}' not found.")
            return False

        for k, v in field_updates.items():
            if isinstance(v, dict) and k in target and isinstance(target[k], dict):
                target[k].update(v)
            else:
                target[k] = v

        self.history.append({
            "action": "mutate_node",
            "node_id": node_id,
            "updates": field_updates,
        })
        logger.info(f"[AgentMemory] Mutated node '{node_id}': {field_updates}")
        return True

    def _find_node_by_id(self, nodes: List[Dict[str, Any]], node_id: str) -> Optional[Dict[str, Any]]:
        """Recursive helper to search AST nodes by ID."""
        for n in nodes:
            if n.get("id") == node_id:
                return n
            if "children" in n and isinstance(n["children"], list):
                res = self._find_node_by_id(n["children"], node_id)
                if res:
                    return res
        return None

    def reset(self):
        """Reset memory session state."""
        self.current_ast = []
        self.generated_code = {"html": "", "css": ""}
        self.similarity_score = 0.0
        self.history = []
        logger.info(f"[AgentMemory] Memory reset for session: {self.session_id}")
