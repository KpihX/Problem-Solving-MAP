"""Cell-level helpers for preprocessing rules."""

from __future__ import annotations

import re
from textwrap import wrap
from typing import Any, Dict, Iterable, Set


def tags_of_cell(cell) -> Set[str]:
	tags = set()
	metadata = getattr(cell, "metadata", {}) or {}
	for tag in metadata.get("tags", []):
		tags.add(str(tag))
	return tags


def should_remove_cell(cell, config: Dict[str, Any]) -> bool:
	remove_tags = set(config.get("remove_cells_with_tag", []))
	return bool(tags_of_cell(cell) & remove_tags)


def should_hide_code(cell, config: Dict[str, Any]) -> bool:
	if cell.cell_type != "code":
		return False
	tags = tags_of_cell(cell)
	hide_tags = set(config.get("hide_code_with_tag", []))
	show_tags = set(config.get("show_outputs_with_tag", []))
	partial_tags = set(config.get("partial_code_with_tag", []))
	
	# Si c'est un masquage partiel, ne pas masquer complètement
	if tags & partial_tags:
		return False
	
	if tags & hide_tags:
		return True
	if config.get("hide_code_by_default", False) and not (tags & show_tags):
		return True
	return False


def should_hide_output(cell, config: Dict[str, Any]) -> bool:
	"""Vérifie si les sorties de la cellule doivent être masquées.
	
	Les sorties sont masquées si la cellule a un tag dans hide_output_with_tag.
	Cela permet de masquer les sorties même si le code reste visible.
	"""
	if cell.cell_type != "code":
		return False
	tags = tags_of_cell(cell)
	hide_output_tags = set(config.get("hide_output_with_tag", []))
	
	return bool(tags & hide_output_tags)


def should_partial_code(cell, config: Dict[str, Any]) -> bool:
	"""Vérifie si le code doit être affiché partiellement."""
	if cell.cell_type != "code":
		return False
	tags = tags_of_cell(cell)
	partial_tags = set(config.get("partial_code_with_tag", []))
	show_tags = set(config.get("show_outputs_with_tag", []))
	
	# Si taguée avec partial_code, activer le partiel
	if tags & partial_tags:
		return True
	
	# Si partial_code_by_default est activé et pas de tag show_output
	if config.get("partial_code_by_default", False) and not (tags & show_tags):
		return True
	
	return False


def apply_partial_code(cell, config: Dict[str, Any]) -> None:
	"""Applique le masquage partiel : garde k premières et n dernières lignes.

	Le séparateur affiché au milieu est personnalisable via
	``partial_code_separator_text`` (par défaut: "# ... [{count} lignes masquées] ...").
	Le placeholder ``{count}`` est remplacé par le nombre de lignes masquées.
	"""
	if cell.cell_type != "code" or not cell.source:
		return

	head_lines = int(config.get("partial_code_head_lines", 2))
	tail_lines = int(config.get("partial_code_tail_lines", 2))

	lines = cell.source.splitlines()
	total = len(lines)

	if total <= head_lines + tail_lines:
		# Trop court pour masquer
		return

	omitted_count = total - head_lines - tail_lines
	head = lines[:head_lines]
	tail = lines[-tail_lines:]

	sep_template = str(
		config.get("partial_code_separator_text", "# ... [{count} lignes masquées] ...")
	)
	sep_line = sep_template.format(count=omitted_count)
	separator = f"\n{sep_line}\n"

	cell.source = "\n".join(head) + separator + "\n".join(tail)

	# Marquer la cellule
	meta = cell.metadata.setdefault("smart_exporter", {})
	meta["partial_code"] = True
	meta["lines_omitted"] = omitted_count


def is_import_only_cell(cell) -> bool:
	if cell.cell_type != "code":
		return False
	pattern = re.compile(r"^\s*(import\s+\w+|from\s+\w+[\.\w]*\s+import\b)")
	lines = [ln for ln in (cell.source or "").splitlines() if ln.strip()]
	if not lines:
		return False
	for line in lines:
		stripped = line.strip()
		if stripped.startswith("#"):
			continue
		if not pattern.match(stripped):
			return False
	return True


def hide_leading_imports(cell, config: Dict[str, Any]) -> None:
	"""Masque les imports au début d'une cellule de code.
	
	Exemple :
	  import numpy as np
	  import pandas as pd
	  
	  def ma_fonction():
	      pass
	
	Devient :
	  def ma_fonction():
	      pass
	"""
	if cell.cell_type != "code" or not cell.source:
		return
	
	if not config.get("hide_leading_imports", True):
		return
	
	lines = cell.source.splitlines()
	import_pattern = re.compile(r"^\s*(import\s+\w+|from\s+\w+[\.\w]*\s+import\b)")
	
	# Trouver où finissent les imports au début
	first_non_import_idx = None
	for i, line in enumerate(lines):
		stripped = line.strip()
		# Ignorer lignes vides et commentaires
		if not stripped or stripped.startswith("#"):
			continue
		# Si ce n'est pas un import, on a trouvé le début du vrai code
		if not import_pattern.match(stripped):
			first_non_import_idx = i
			break
	
	# Si tout est import ou pas d'imports, ne rien faire
	if first_non_import_idx is None or first_non_import_idx == 0:
		return
	
	# Garder seulement à partir du premier non-import
	# Supprimer aussi les lignes vides qui précèdent
	remaining_lines = lines[first_non_import_idx:]
	
	# Supprimer les lignes vides au début du résultat
	while remaining_lines and not remaining_lines[0].strip():
		remaining_lines.pop(0)
	
	cell.source = "\n".join(remaining_lines)
	
	# Marquer dans les métadonnées
	meta = cell.metadata.setdefault("smart_exporter", {})
	meta["leading_imports_hidden"] = True


def reflow_markdown_cell(md_text: str, config: Dict[str, Any]) -> str:
	max_len = int(config.get("max_line_length", 120))
	lines = md_text.splitlines()
	out_lines = []
	in_fence = False
	fence_re = re.compile(r"^\s*```")
	paragraph: list[str] = []

	def flush_paragraph():
		if not paragraph:
			return
		combined = " ".join(line.strip() for line in paragraph)
		# N'effectue des retours à la ligne que sur les espaces, jamais en
		# coupant un mot ou sur des tirets afin d'éviter tout "tronquage" visuel.
		wrapped = wrap(
			combined,
			width=max_len,
			break_long_words=False,
			break_on_hyphens=False,
		) or [combined]
		out_lines.extend(wrapped)
		paragraph.clear()

	for line in lines:
		if fence_re.match(line):
			flush_paragraph()
			out_lines.append(line)
			in_fence = not in_fence
			continue
		if in_fence:
			out_lines.append(line)
			continue
		if not line.strip():
			flush_paragraph()
			out_lines.append("")
		else:
			paragraph.append(line)
	flush_paragraph()
	return "\n".join(out_lines)


def mark_cell_with_long_lines(cell, config: Dict[str, Any]) -> bool:
	if cell.cell_type != "code":
		return False
	threshold = int(config.get("long_line_threshold", 100))
	for line in (cell.source or "").splitlines():
		if len(line) > threshold:
			return True
	return False
