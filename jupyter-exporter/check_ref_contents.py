"""Check exact reference contents."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ipynb_smart_exporter.utils.reference_manager import ReferenceManager

# Load notebook
notebook_path = Path("case/RandomAlgorithms.ipynb")
with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

cells = notebook['cells']

rm = ReferenceManager()
rm.build_global_reference_map(cells)

print("EXACT REFERENCE CONTENTS:")
print("="*80)
for i, ref in enumerate(rm.global_order, 1):
    print(f"\n[{i}] Cell {ref.cell_index}, local {ref.local_id}:")
    print(f"Content: «{ref.definition}»")
    print(f"Length: {len(ref.definition)} chars")
