"""HTML conversion helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from jinja2 import Template
from nbconvert import HTMLExporter
from traitlets.config import Config

from .utils.document_structure import (
	add_heading_ids,
	extract_headings,
	generate_cover_html,
	generate_toc_html,
)


def fix_relative_image_paths(html: str, notebook_path: Path) -> str:
	"""Fix relative image paths in HTML to be absolute or relative to output."""
	notebook_dir = notebook_path.parent
	
	# Pattern to match img tags with relative src
	pattern = r'<img\s+[^>]*src="([^"]+)"[^>]*>'
	
	def replace_src(match):
		img_tag = match.group(0)
		src = match.group(1)
		
		# Skip if already absolute (http://, https://, data:, /)
		if src.startswith(('http://', 'https://', 'data:', '/', '#')):
			return img_tag
		
		# Convert relative path to absolute
		img_path = notebook_dir / src
		if img_path.exists():
			# Keep as relative path from the notebook directory
			return img_tag
		
		return img_tag
	
	return re.sub(pattern, replace_src, html)


def style_partial_code_separators(html: str) -> str:
	"""Add special styling to partial code separator comments."""
	# Pattern to find comment lines with "lignes omises" or similar
	pattern = r'(<span class="hljs-comment">)(#[^<]*(?:lignes omises|lines omitted|═══)[^<]*)(</span>)'
	
	def wrap_separator(match):
		open_tag = match.group(1)
		content = match.group(2)
		close_tag = match.group(3)
		return f'{open_tag}<span class="code-omission-separator">{content}</span>{close_tag}'
	
	return re.sub(pattern, wrap_separator, html, flags=re.IGNORECASE)


def notebook_to_html(nb, config: Dict[str, Any], notebook_path: Path | None = None) -> str:
	"""Render a notebook node to HTML using nbconvert and a template."""
	exporter_cfg = Config()
	exporter_cfg.HTMLExporter.exclude_input = False
	
	# Utiliser TagRemovePreprocessor pour retirer l'input des cellules taguées
	# (voir preprocessor._mark_hidden qui ajoute le tag 'remove_input').
	exporter_cfg.TagRemovePreprocessor = Config()
	exporter_cfg.TagRemovePreprocessor.enabled = True
	exporter_cfg.TagRemovePreprocessor.remove_input_tags = {"remove_input"}
	exporter_cfg.HTMLExporter.preprocessors = [
		"nbconvert.preprocessors.TagRemovePreprocessor"
	]
	
	exporter = HTMLExporter(config=exporter_cfg)
	body, resources = exporter.from_notebook_node(nb)

	# Fix relative image paths if notebook path is provided
	if notebook_path:
		body = fix_relative_image_paths(body, Path(notebook_path))

	# Style partial code separators
	body = style_partial_code_separators(body)

	# Add IDs to headings for TOC linking
	body = add_heading_ids(body)

	# Generate cover page if enabled
	cover_html = ""
	if config.get("generate_cover", False):
		cover_html = generate_cover_html(config)

	# Generate TOC if enabled
	toc_html = ""
	if config.get("generate_toc", False):
		headings = extract_headings(body, config.get("toc_depth", 3))
		if headings:
			toc_html = generate_toc_html(headings, config)

	# Combine cover, TOC, and body
	full_body = cover_html + toc_html + body

	template_text = Path(config["template"]).read_text(encoding="utf-8")
	template = Template(template_text)

	css_blocks = []
	for css_path in config.get("css_files", []):
		path_obj = Path(css_path)
		if path_obj.exists():
			css_blocks.append(path_obj.read_text(encoding="utf-8"))
	
	# Injection des marges PDF personnalisées et en-tête de page
	page_header_text = config.get("page_header", "") or config.get("cover_title", "")
	text_font_family = config.get('text_font_family', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif')
	code_font_family = config.get('code_font_family', '"Menlo", "Consolas", "DejaVu Sans Mono", monospace')
	margin_css = f"""
	:root {{
		--pdf-margin-top: {config.get('pdf_margin_top', '2cm')};
		--pdf-margin-right: {config.get('pdf_margin_right', '2cm')};
		--pdf-margin-bottom: {config.get('pdf_margin_bottom', '2cm')};
		--pdf-margin-left: {config.get('pdf_margin_left', '2cm')};
		--page-header-text: "{page_header_text.replace('"', '\\"')}";
		--text-font-family: {text_font_family};
		--text-font-size: {config.get('text_font_size', '11pt')};
		--text-line-height: {config.get('text_line_height', '1.6')};
		--code-font-family: {code_font_family};
		--code-font-size: {config.get('code_font_size', '9pt')};
	}}
	"""
	css_blocks.insert(0, margin_css)
	
	# CSS final pour forcer les variables et écraser le CSS de JupyterLab/nbconvert
	# Séparer clairement : text_font_size pour markdown, code_font_size pour code
	final_override_css = f"""
	/* === TEXTE MARKDOWN SEULEMENT === */
	body {{
		font-family: {text_font_family} !important;
		font-size: {config.get('text_font_size', '11pt')} !important;
		line-height: {config.get('text_line_height', '1.6')} !important;
	}}
	
	/* Forcer text_font_size sur tous les éléments de texte/markdown */
	p, li, td, th, div.text_cell_render, .jp-RenderedHTMLCommon, .jp-RenderedMarkdown,
	div.jp-MarkdownOutput, .jp-RenderedText {{
		font-size: {config.get('text_font_size', '11pt')} !important;
		line-height: {config.get('text_line_height', '1.6')} !important;
	}}
	
	/* === CODE SEULEMENT === */
	/* Forcer code_font_size sur TOUS les éléments de code (input + output) */
	.cm-editor,
	.cm-editor.cm-s-jupyter,
	.cm-editor.cm-s-jupyter .highlight pre,
	.cm-s-jupyter .CodeMirror-line,
	div.input_area pre,
	.jp-InputArea pre,
	.jp-InputArea-editor,
	div.output_area pre,
	.jp-OutputArea-output pre,
	.jp-RenderedText pre,
	.highlight pre,
	pre code,
	pre.highlight {{
		font-family: {code_font_family} !important;
		font-size: {config.get('code_font_size', '9pt')} !important;
	}}
	"""
	css_blocks.append(final_override_css)
	
	# Classe pour masquer les compteurs si demandé
	body_class = ""
	if config.get("hide_execution_count", False):
		body_class = ' class="hide-execution-count"'

	html = template.render(
		body=full_body,
		body_class=body_class,
		head_css="\n".join(f"<style>\n{chunk}\n</style>" for chunk in css_blocks),
	)
	return html
