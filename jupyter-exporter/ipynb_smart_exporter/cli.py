"""Command-line interface for ipynb-smart-exporter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .converter_html import notebook_to_html
from .converter_pdf import html_to_pdf
from .preprocessor import preprocess_notebook
from .utils.logging_util import setup_logger
from .utils.notebook_loader import load_notebook


logger = setup_logger("ipynb_smart_exporter.cli")


def build_parser() -> argparse.ArgumentParser:
	"""Create an argument parser so it can be reused in tests."""
	parser = argparse.ArgumentParser(
		description="Intelligent IPYNB to PDF/HTML exporter."
	)
	parser.add_argument("input", help="Path to the source .ipynb notebook")
	parser.add_argument(
		"--config",
		help="Optional YAML config file overriding defaults",
		default=None,
	)
	parser.add_argument(
		"--output",
		"-o",
		help="Output PDF file path",
		default="output.pdf",
	)
	parser.add_argument(
		"--html-output",
		help="If provided, dump the intermediate HTML to this path for inspection",
		default=None,
	)
	parser.add_argument(
		"--log-level",
		help="Logging level (DEBUG, INFO, WARNING, ERROR)",
		default="INFO",
	)
	return parser


def main(argv: list[str] | None = None) -> int:
	"""CLI entry point used by console script."""
	parser = build_parser()
	args = parser.parse_args(argv if argv is not None else sys.argv[1:])

	logger.setLevel(args.log_level.upper())

	config = load_config(args.config)
	logger.info("Loaded configuration from %s", args.config or "defaults")

	notebook = load_notebook(args.input)
	logger.info("Notebook loaded: %s", args.input)

	processed = preprocess_notebook(notebook, config)
	logger.info("Preprocessing complete (%s cells)", len(processed.cells))

	html = notebook_to_html(processed, config, Path(args.input))
	logger.info("HTML conversion finished (length=%s)", len(html))

	if args.html_output:
		Path(args.html_output).write_text(html, encoding="utf-8")
		logger.info("Intermediate HTML saved to %s", args.html_output)

	html_to_pdf(html, args.output, config)
	logger.info("PDF written to %s", args.output)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
