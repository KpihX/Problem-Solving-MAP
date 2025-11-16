"""Configuration helpers for ipynb-smart-exporter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parent

DEFAULT_CONFIG: Dict[str, Any] = {
	"hide_code_by_default": False,
	"partial_code_by_default": False,  # If True, show only first/last lines of code
	"remove_cells_with_tag": ["remove"],
	"hide_code_with_tag": ["hide_code"],
	"hide_output_with_tag": ["hide_output"],  # Hide outputs even if code is visible
	"show_outputs_with_tag": ["show_output"],
	"partial_code_with_tag": ["partial_code"],
	"reflow_markdown": True,
	"max_line_length": 120,
	"css_files": [
		str(PACKAGE_ROOT / "css" / "base.css"),
		str(PACKAGE_ROOT / "css" / "code_formatting.css"),
		str(PACKAGE_ROOT / "css" / "document_structure.css"),
	],
	"template": str(PACKAGE_ROOT / "templates" / "base_template.html"),
	"detect_long_code_lines": True,
	"long_line_threshold": 100,
	"hide_import_only_cells": True,
	"hide_leading_imports": True,  # Hide import statements at the beginning of code cells
	"page_break_marker": "<!-- PAGE_BREAK -->",  # Marker for manual page breaks in markdown
	"hide_execution_count": False,
	"partial_code_head_lines": 2,
	"partial_code_tail_lines": 2,
	"partial_code_separator_text": "# ═══ [{count} lignes omises] ═══",
	"pdf_margin_top": "2cm",
	"pdf_margin_right": "2cm",
	"pdf_margin_bottom": "2cm",
	"pdf_margin_left": "2cm",
	# Typography
	"text_font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
	"text_font_size": "11pt",
	"text_line_height": "1.6",
	"code_font_family": "'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace",
	"code_font_size": "9pt",
	# Output filtering
	"hide_warnings": True,
	"hide_errors": False,
	"warning_patterns": [
		"Warning",
		"DeprecationWarning",
		"FutureWarning",
		"UserWarning",
	],
	# Table of Contents
	"generate_toc": False,
	"toc_depth": 3,
	"toc_title": "Table des matières",
	# Cover page
	"generate_cover": False,
	"cover_title": "",
	"cover_subtitle": "",
	"cover_author": "",  # Legacy single author (deprecated, use cover_authors)
	"cover_authors": [],  # List of authors (preferred)
	"cover_institution": "",
	"cover_subject": "",
	"cover_date": "auto",
	"cover_logo": "",
		"cover_quote": "",  # Optional quote/citation at bottom
	# Page numbering
	"page_numbering": True,
	"page_number_format": "Page {page} / {total}",
	"page_number_position": "bottom-right",
	# Page header (appears on all pages after TOC)
	"page_header": "",  # If empty, uses cover_title by default
	# Scientific features
	"figure_numbering": True,
	"equation_numbering": False,
	"add_bibliography": False,
	# Bibliographic references
	"centralize_references": True,  # Consolidate all markdown references to end of document
}


def _resolve_path(base: Path, raw_path: str) -> str:
	path = Path(raw_path)
	if path.is_absolute():
		return str(path)
	candidate = (base / path).resolve()
	if candidate.exists():
		return str(candidate)
	return str(path)


def _resolve_resource_paths(cfg: Dict[str, Any], config_dir: Path | None) -> Dict[str, Any]:
	resolved = cfg.copy()
	base = config_dir or PACKAGE_ROOT
	resolved["template"] = _resolve_path(base, resolved["template"])
	resolved["css_files"] = [
		_resolve_path(base, css_path) for css_path in resolved.get("css_files", [])
	]
	return resolved


def load_config(path: str | None) -> Dict[str, Any]:
	"""Load YAML config from *path* if provided and merge with defaults."""
	config_dir = None
	cfg = DEFAULT_CONFIG.copy()
	if path is not None:
		config_path = Path(path)
		if not config_path.exists():
			raise FileNotFoundError(f"Config file not found: {path}")
		config_dir = config_path.parent
		with config_path.open("r", encoding="utf-8") as stream:
			user_cfg = yaml.safe_load(stream) or {}
		cfg.update(user_cfg)
	return _resolve_resource_paths(cfg, config_dir)
