"""Notebook metadata helpers."""

from __future__ import annotations

from typing import Any, Dict


def get_notebook_metadata(nb) -> Dict[str, Any]:
	"""Return the optional ``smart_exporter`` metadata section."""
	if hasattr(nb, "metadata") and isinstance(nb.metadata, dict):
		return nb.metadata.get("smart_exporter", {}) or {}
	return {}
