"""Notebook loading helper."""

from __future__ import annotations

from pathlib import Path

import nbformat


def load_notebook(path: str):
	"""Load a notebook file and return a nbformat NotebookNode."""
	notebook_path = Path(path)
	if not notebook_path.exists():
		raise FileNotFoundError(f"Notebook file not found: {path}")
	return nbformat.read(notebook_path, as_version=4)
