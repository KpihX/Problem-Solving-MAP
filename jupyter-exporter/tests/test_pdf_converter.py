"""Smoke tests for PDF conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from ipynb_smart_exporter.config import DEFAULT_CONFIG
from ipynb_smart_exporter.converter_pdf import html_to_pdf


def test_html_to_pdf_writes_file(tmp_path):
	pytest.importorskip("weasyprint")
	html = "<html><body><p>Test PDF</p></body></html>"
	output = tmp_path / "out.pdf"
	html_to_pdf(html, str(output), DEFAULT_CONFIG)
	assert output.exists()
	assert output.stat().st_size > 0
