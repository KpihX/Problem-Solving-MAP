"""Detailed analysis of reference extraction."""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ipynb_smart_exporter.utils.reference_manager import ReferenceManager

def analyze_notebook():
    """Analyze all references in the notebook."""
    # Load notebook
    notebook_path = Path("case/RandomAlgorithms.ipynb")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = notebook['cells']
    print(f"Total cells: {len(cells)}\n")
    
    rm = ReferenceManager()
    
    print("="*80)
    print("SCANNING ALL MARKDOWN CELLS FOR REFERENCES")
    print("="*80)
    
    all_cited_refs = set()
    all_defined_refs = {}
    
    for i, cell in enumerate(cells):
        if cell['cell_type'] != 'markdown':
            continue
        
        markdown_text = ''.join(cell.get('source', []))
        
        # Find citations
        citations = list(rm.CITATION_PATTERN.finditer(markdown_text))
        # Find definitions
        definitions = list(rm.DEFINITION_START_PATTERN.finditer(markdown_text))
        
        if citations or definitions:
            print(f"\n--- Cell {i} ---")
            
            if citations:
                print(f"  Citations found: {len(citations)}")
                for match in citations:
                    local_num = match.group(1)
                    ref_id = match.group(2)
                    context = markdown_text[max(0, match.start()-30):match.end()+30]
                    print(f"    [[{local_num}]](#{ref_id}) in: ...{context}...")
                    all_cited_refs.add(ref_id)
            
            if definitions:
                print(f"  Definitions found: {len(definitions)}")
                for match in definitions:
                    ref_id = match.group(1)
                    local_num = match.group(2)
                    definition_start = match.group(3)[:60]
                    print(f"    <a id=\"{ref_id}\"></a>[{local_num}] {definition_start}...")
                    all_defined_refs[ref_id] = local_num
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total unique ref_ids cited: {len(all_cited_refs)}")
    print(f"Cited refs: {sorted(all_cited_refs)}")
    print(f"\nTotal unique ref_ids defined: {len(all_defined_refs)}")
    print(f"Defined refs: {sorted(all_defined_refs.keys())}")
    
    # Check for mismatches
    cited_not_defined = all_cited_refs - set(all_defined_refs.keys())
    defined_not_cited = set(all_defined_refs.keys()) - all_cited_refs
    
    if cited_not_defined:
        print(f"\n⚠️  Cited but not defined: {cited_not_defined}")
    if defined_not_cited:
        print(f"\n⚠️  Defined but not cited: {defined_not_cited}")
    
    print("\n" + "="*80)
    print("TESTING REFERENCE MANAGER")
    print("="*80)
    
    rm2 = ReferenceManager()
    rm2.build_global_reference_map(cells)
    
    print(f"Global order length: {len(rm2.global_order)}")
    print(f"Global order: {rm2.global_order}")
    print(f"\nUnique references stored: {len(rm2.unique_references)}")
    for i, ref in enumerate(rm2.global_order, 1):
        print(f"  [{i}] Cell {ref.cell_index}, local ref{ref.local_num}: {ref.definition[:80]}...")
    
    print(f"\nCell-local mappings: {len(rm2.cell_local_refs)}")
    for (cell_idx, local_num), ref in sorted(rm2.cell_local_refs.items()):
        print(f"  Cell {cell_idx}, local_num [{local_num}] -> global ref {ref.global_num}")

if __name__ == '__main__':
    analyze_notebook()
