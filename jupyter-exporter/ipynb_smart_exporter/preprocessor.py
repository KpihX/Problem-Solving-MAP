"""Notebook preprocessing pipeline."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from .metadata import get_notebook_metadata
from .utils.cell_operations import (
	apply_partial_code,
	hide_leading_imports,
	is_import_only_cell,
	mark_cell_with_long_lines,
	reflow_markdown_cell,
	should_hide_code,
	should_hide_output,
	should_partial_code,
	should_remove_cell,
)
from .utils.output_filter import filter_output_text
from .utils.reference_manager import ReferenceManager


def _mark_hidden(cell, reason: str) -> None:
	meta = cell.metadata.setdefault("smart_exporter", {})
	meta["hidden_reason"] = reason
	tags = cell.metadata.setdefault("tags", [])
	if "hidden" not in tags:
		tags.append("hidden")
	# Ajouter un tag spécifique que nbconvert utilisera pour retirer l'input
	# via TagRemovePreprocessor (configuré dans converter_html).
	if "remove_input" not in tags:
		tags.append("remove_input")


def preprocess_notebook(nb, config: Dict[str, Any]):
	"""Return a processed copy of the notebook using *config* rules."""
	notebook = deepcopy(nb)
	merged_cfg = config.copy()
	merged_cfg.update(get_notebook_metadata(notebook))

	# === GESTION DES RÉFÉRENCES BIBLIOGRAPHIQUES ===
	# Centraliser toutes les références à la fin du document
	if merged_cfg.get("centralize_references", True):
		ref_manager = ReferenceManager()
		ref_manager.process_notebook(notebook)

	new_cells = []
	for cell in notebook.cells:
		if should_remove_cell(cell, merged_cfg):
			continue

		if (
			merged_cfg.get("hide_import_only_cells", True)
			and cell.cell_type == "code"
			and is_import_only_cell(cell)
		):
			# Ne pas laisser une cellule vide grisée : on marque pour suppression
			# de l'input par le template/preprocessor.
			_mark_hidden(cell, "import_only")

		# Masquage des imports en début de cellule de code (AVANT partial_code)
		if cell.cell_type == "code" and merged_cfg.get("hide_leading_imports", True):
			hide_leading_imports(cell, merged_cfg)
		
		# Gestion du masquage partiel (APRÈS hide_leading_imports)
		if cell.cell_type == "code" and should_partial_code(cell, merged_cfg):
			apply_partial_code(cell, merged_cfg)

		if cell.cell_type == "code" and should_hide_code(cell, merged_cfg):
			# Laisser le code intact mais taguer pour suppression d'input plus tard
			# afin d'éviter tout bloc vide.
			_mark_hidden(cell, "hide_code_rule")
		
		# Masquage des sorties avec tag spécifique (même si code visible)
		if cell.cell_type == "code" and should_hide_output(cell, merged_cfg):
			# Vider toutes les sorties de la cellule
			if hasattr(cell, "outputs"):
				cell.outputs = []
			# Marquer dans les métadonnées
			meta = cell.metadata.setdefault("smart_exporter", {})
			meta["output_hidden"] = True

		# Filter warnings/errors from cell outputs (only for stderr streams)
		if cell.cell_type == "code" and hasattr(cell, "outputs") and merged_cfg.get("hide_warnings", False):
			for output in cell.outputs:
				# Only filter stderr streams, not stdout
				if output.get("output_type") == "stream" and output.get("name") == "stderr":
					if "text" in output:
						output["text"] = filter_output_text(
							output["text"],
							merged_cfg.get("hide_warnings", False),
							merged_cfg.get("hide_errors", False),
							merged_cfg.get("warning_patterns", [])
						)
				# Filter error tracebacks if requested
				elif output.get("output_type") == "error" and merged_cfg.get("hide_errors", False):
					if "traceback" in output:
						output["traceback"] = []

		if cell.cell_type == "markdown" and merged_cfg.get("reflow_markdown", True):
			cell.source = reflow_markdown_cell(cell.source, merged_cfg)
		
		# Gestion du saut de page avec marqueur spécial
		if cell.cell_type == "markdown":
			page_break_marker = merged_cfg.get("page_break_marker", "<!-- PAGE_BREAK -->")
			if page_break_marker in cell.source:
				# Remplacer le marqueur par un div avec classe CSS pour saut de page
				cell.source = cell.source.replace(
					page_break_marker,
					'<div style="page-break-after: always;"></div>'
				)

		if cell.cell_type == "code" and merged_cfg.get("detect_long_code_lines", True):
			if mark_cell_with_long_lines(cell, merged_cfg):
				cell.metadata.setdefault("smart_exporter", {})["long_lines"] = True

		new_cells.append(cell)

	notebook.cells = new_cells
	notebook.metadata.setdefault("smart_exporter", {}).update(merged_cfg)
	return notebook
