"""Test the complete reference processing pipeline."""

import nbformat
from ipynb_smart_exporter.utils.reference_manager import ReferenceManager

# Load notebook
with open('case/RandomAlgorithms.ipynb', 'r', encoding='utf-8') as f:
    notebook = nbformat.read(f, as_version=4)

print(f"Total cells before processing: {len(notebook.cells)}")

# Check cell 47 (last one with references) before processing
print("\n=== CELL 47 BEFORE PROCESSING ===")
cell_47 = notebook.cells[47]
print(f"Cell type: {cell_47.cell_type}")
if cell_47.cell_type == 'markdown':
    source = cell_47.source
    print(f"Length: {len(source)}")
    print("Last 500 chars:")
    print(source[-500:])
    print("\n" + "="*80 + "\n")

# Process with ReferenceManager
ref_manager = ReferenceManager()
ref_manager.process_notebook(notebook)

print(f"Total cells after processing: {len(notebook.cells)}")
print(f"References found: {len(ref_manager.global_order)}")

# Check cell 47 after processing
print("\n=== CELL 47 AFTER PROCESSING ===")
cell_47_after = notebook.cells[47]
if cell_47_after.cell_type == 'markdown':
    source_after = cell_47_after.source
    print(f"Length: {len(source_after)}")
    print("Last 500 chars:")
    print(source_after[-500:])
    print("\n" + "="*80 + "\n")

# Check the new references cell (should be cell 48)
print("\n=== NEW REFERENCES CELL (CELL 48) ===")
if len(notebook.cells) > 48:
    refs_cell = notebook.cells[48]
    print(f"Cell type: {refs_cell.cell_type}")
    if refs_cell.cell_type == 'markdown':
        print("Full content:")
        print(refs_cell.source)
else:
    print("ERROR: No cell 48 found!")
