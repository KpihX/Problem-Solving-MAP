"""Debug script to see what's happening with reference removal."""

import nbformat
from ipynb_smart_exporter.utils.reference_manager import ReferenceManager

# Load notebook
with open('case/RandomAlgorithms.ipynb', 'r', encoding='utf-8') as f:
    notebook = nbformat.read(f, as_version=4)

# Find cells with reference definitions
ref_manager = ReferenceManager()

print("=== CELLS WITH REFERENCE DEFINITIONS ===\n")
for idx, cell in enumerate(notebook.cells):
    if cell.cell_type != 'markdown':
        continue
    
    source = cell.source
    
    # Check if cell has reference definitions
    if '<a id="ref' in source:
        print(f"Cell {idx} (first 200 chars):")
        print(source[:200])
        print("\n" + "="*60 + "\n")
        
        # Try removing references
        cleaned = ref_manager.remove_reference_section(source)
        print(f"After removal (first 200 chars):")
        print(cleaned[:200])
        print("\n" + "="*60 + "\n")
        print(f"Original length: {len(source)}, Cleaned length: {len(cleaned)}")
        print("\n" + "="*80 + "\n\n")
