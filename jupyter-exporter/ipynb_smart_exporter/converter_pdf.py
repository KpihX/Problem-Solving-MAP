"""PDF conversion helpers using WeasyPrint or Playwright."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Iterable

try:  # pragma: no cover - exercised via integration tests
	from weasyprint import CSS, HTML
except ImportError as exc:  # pragma: no cover
	CSS = HTML = None  # type: ignore
	_IMPORT_ERROR = exc
else:
	_IMPORT_ERROR = None

try:
	from playwright.sync_api import sync_playwright
	_PLAYWRIGHT_AVAILABLE = True
except ImportError:
	_PLAYWRIGHT_AVAILABLE = False


def _load_stylesheets(paths: Iterable[str]):
	if CSS is None:  # pragma: no cover
		return []
	sheets = []
	for css_path in paths:
		path = Path(css_path)
		if path.exists():
			sheets.append(CSS(filename=str(path)))
	return sheets


def html_to_pdf_playwright(html_path: str, output_path: str, config: Dict[str, Any]) -> None:
	"""Generate PDF using Playwright (renders MathJax correctly)."""
	if not _PLAYWRIGHT_AVAILABLE:
		raise RuntimeError(
			"Playwright is not installed. Install with: pip install playwright && playwright install chromium"
		)
	
	with sync_playwright() as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		
		# Load HTML file
		page.goto(f"file://{Path(html_path).absolute()}")
		
		# Wait for MathJax to render (important!)
		time.sleep(2)  # Give MathJax time to process
		try:
			page.wait_for_function("window.MathJax && window.MathJax.typesetPromise", timeout=5000)
			page.evaluate("window.MathJax.typesetPromise()")
			time.sleep(1)  # Wait for typeset to complete
		except Exception:
			pass  # Continue even if MathJax wait fails
		
		# Generate PDF with proper margins
		margin = {
			'top': config.get('pdf_margin_top', '2cm'),
			'right': config.get('pdf_margin_right', '2cm'),
			'bottom': config.get('pdf_margin_bottom', '2cm'),
			'left': config.get('pdf_margin_left', '2cm'),
		}
		
		page.pdf(
			path=output_path,
			format='A4',
			margin=margin,
			print_background=True,
			scale=0.95
		)
		
		browser.close()


def html_to_pdf(html_string: str, output_path: str, config: Dict[str, Any]) -> None:
	"""Write *html_string* to *output_path* as a PDF.
	
	Uses Playwright if available (for MathJax rendering), otherwise WeasyPrint.
	"""
	output = Path(output_path)
	output.parent.mkdir(parents=True, exist_ok=True)
	
	# Try Playwright first (supports MathJax)
	if _PLAYWRIGHT_AVAILABLE:
		# Save HTML to temp file
		temp_html = output.parent / f"{output.stem}_temp.html"
		temp_html.write_text(html_string, encoding="utf-8")
		try:
			html_to_pdf_playwright(str(temp_html), str(output), config)
			temp_html.unlink()  # Clean up
			return
		except Exception as e:
			temp_html.unlink()  # Clean up
			print(f"Playwright PDF generation failed: {e}")
			print("Falling back to WeasyPrint (MathJax will not render)")
	
	# Fallback to WeasyPrint
	if HTML is None:  # pragma: no cover
		raise RuntimeError(
			"WeasyPrint is required for PDF export"
		) from _IMPORT_ERROR

	stylesheets = _load_stylesheets(config.get("css_files", []))
	HTML(string=html_string).write_pdf(str(output), stylesheets=stylesheets)
