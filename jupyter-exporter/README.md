# ipynb-smart-exporter

Intelligent `.ipynb` → HTML/PDF exporter with scientific publishing features.

## Features

### Core Functionality

- ✅ **Smart preprocessing**: Keep/drop cells via tags, hide code while keeping outputs
- ✅ **Professional styling**: Premium typography with Charter, Lato, and Fira Code fonts
- ✅ **MathJax rendering**: Perfect LaTeX equations via Playwright/Chromium
- ✅ **Code formatting**: Syntax highlighting, partial code masking, long line detection

### Scientific Publishing

- ✅ **Table of Contents**: Auto-generated from headings with clickable links
- ✅ **Cover Page**: Professional design with title, author, institution, date
- ✅ **Page Numbering**: Customizable footer with page numbers
- ✅ **Warning Filtering**: Hide Python warnings and errors from outputs
- ✅ **Figure Numbering**: Automatic figure and equation numbering
- ✅ **Markdown Reflow**: Prevent text overflow in PDF

## Installation

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Required Dependencies

**For MathJax rendering (recommended):**
```bash
pip install playwright
playwright install chromium
```

**For WeasyPrint (fallback):**
On Windows:
```powershell
winget install -e --id=tschoonj.GTKForWindows
```

On Linux/macOS, follow the [official guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#install-weasyprint).

## Quick Start

### Basic Usage

```bash
python -m ipynb_smart_exporter.cli notebook.ipynb \
  --config config.yaml \
  --output output.pdf \
  --html-output output.html
```

### Scientific Document Example

```bash
python -m ipynb_smart_exporter.cli case/RandomAlgorithms.ipynb \
  --config case/config_RandomAlgorithms.yaml \
  --output case/RandomAlgorithms.pdf
```

## Configuration

### Essential Options

```yaml
# Appearance
hide_execution_count: true          # Hide In[]/Out[] counters
hide_code_by_default: false         # Show/hide code cells

# Scientific Features
generate_cover: true                # Enable cover page
cover_title: "Your Title"
cover_author: "Your Name"
cover_institution: "Institution"

generate_toc: true                  # Table of contents
toc_depth: 3                        # Max heading level

hide_warnings: true                 # Filter Python warnings
page_numbering: true                # Page numbers
figure_numbering: true              # Auto-number figures

# PDF Margins
pdf_margin_top: 2cm
pdf_margin_right: 2.5cm
pdf_margin_bottom: 2cm
pdf_margin_left: 2.5cm

# Styling
css_files:
  - ipynb_smart_exporter/css/base.css
  - ipynb_smart_exporter/css/code_formatting.css
  - ipynb_smart_exporter/css/premium_typography.css
  - ipynb_smart_exporter/css/document_structure.css
```

### Cell Tags

Tag cells in Jupyter via **View → Cell Toolbar → Tags**:

| Tag | Effect |
|-----|--------|
| `remove` | Drop cell entirely |
| `hide_code` | Hide code, keep output |
| `partial_code` | Show first/last lines only |
| `show_output` | Force output visibility |

### Advanced Configuration

See `case/config_RandomAlgorithms.yaml` for a complete example with all scientific features enabled.

## Architecture

```
Notebook (.ipynb)
  ↓
Preprocessing (filter warnings, mask code)
  ↓
HTML Generation (cover page, TOC, content)
  ↓
PDF Generation (Playwright with MathJax or WeasyPrint)
```

## Testing

```bash
pytest
pytest --maxfail=1 --disable-warnings -q
```

## Example Output

The `case/` directory contains a complete scientific notebook (`RandomAlgorithms.ipynb`) with:
- Complex LaTeX equations
- Multiple figures and plots
- Algorithm implementations
- Mathematical proofs

Run the conversion to see all features in action!

## License

MIT
- Plugin API for custom rules (e.g., hide cells by regex)
- Alternative PDF backend (wkhtmltopdf, Paged.js, PrinceXML)
- GitHub Action workflow that runs tests and publishes wheels

## License

Released under the MIT License. See `LICENSE`.
