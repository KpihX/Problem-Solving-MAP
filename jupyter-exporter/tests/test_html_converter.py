"""Tests for HTML conversion."""

from __future__ import annotations

import nbformat

from ipynb_smart_exporter.config import DEFAULT_CONFIG
from ipynb_smart_exporter.converter_html import notebook_to_html


def test_notebook_to_html_contains_template_wrappers():
	nb = nbformat.v4.new_notebook()
	nb.cells = [nbformat.v4.new_markdown_cell("Hello **world**!")]
	html = notebook_to_html(nb, DEFAULT_CONFIG)
	assert "<html" in html
	assert "Hello" in html
