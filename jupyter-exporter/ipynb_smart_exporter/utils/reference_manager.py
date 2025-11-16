"""
Module for managing bibliographic references in markdown cells.

This module centralizes all references from individual markdown cells into a single
references section at the end of the document. It handles:
- Extracting reference citations [[1]](#ref1) from text
- Extracting reference definitions <a id="ref1"></a>[1] from cell footers
- Creating a global reference mapping by order of first appearance
- Updating citation numbers throughout the document
- Removing local reference sections
- Adding a final consolidated references section
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple, Set
from collections import OrderedDict


class Reference:
    """Represents a bibliographic reference."""
    
    def __init__(self, local_id: str, local_num: int, definition: str, cell_index: int):
        """
        Args:
            local_id: The local anchor ID in the cell (e.g., "ref1")
            local_num: The local reference number in the cell (e.g., 1)
            definition: The full reference text
            cell_index: The cell where this reference is defined
        """
        self.local_id = local_id
        self.local_num = local_num
        self.definition = definition.strip()
        self.global_num = None  # Will be assigned later
        self.cell_index = cell_index
    
    @staticmethod
    def normalize_for_dedup(text: str) -> str:
        """
        Normalize reference text for deduplication.
        
        Removes:
        - Explanatory notes in parentheses at the end
        - PAGE_BREAK markers
        - Extra whitespace
        
        Args:
            text: Reference definition text
        
        Returns:
            Normalized text for comparison
        """
        import re
        
        # Remove PAGE_BREAK markers
        text = re.sub(r'<!--\s*PAGE_BREAK\s*-->', '', text)
        
        # Remove trailing parenthetical notes
        # This matches parentheses at the end with any content
        text = re.sub(r'\s*\([^)]+\)\s*\.?\s*$', '.', text)
        
        # Normalize multiple dots to single dot
        text = re.sub(r'\.+', '.', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def __repr__(self):
        return f"Reference(cell={self.cell_index}, local={self.local_num}, global={self.global_num}, id={self.local_id})"
    
    def __hash__(self):
        # Hash by normalized definition for deduplication
        return hash(self.normalize_for_dedup(self.definition))
    
    def __eq__(self, other):
        # Two references are equal if they have the same normalized definition
        if not isinstance(other, Reference):
            return False
        return self.normalize_for_dedup(self.definition) == self.normalize_for_dedup(other.definition)


class ReferenceManager:
    """Manages the extraction, remapping, and consolidation of references."""
    
    # Regex patterns
    # Match citations in text: [[1]](#ref1) or [[2]](#ref2), etc.
    CITATION_PATTERN = re.compile(r'\[\[(\d+)\]\]\(#(ref\d+)\)')
    
    # Match reference definitions: <a id="ref1"></a>[1] Author, Title...
    # Can span multiple lines, ends at next reference or end of section
    DEFINITION_START_PATTERN = re.compile(r'<a\s+id="(ref\d+)"\s*></a>\[(\d+)\]\s*(.+)', re.MULTILINE)
    
    # Match the separator before references section
    REFERENCE_SECTION_PATTERN = re.compile(
        r'^\s*---\s*\n\s*\*\*Références\s*:\*\*\s*\n',
        re.MULTILINE
    )
    
    def __init__(self):
        """Initialize the reference manager."""
        # Maps definition text -> Reference object (for deduplication)
        self.unique_references: Dict[str, Reference] = {}
        
        # Maps (cell_index, local_num) -> Reference object (for citation lookup by NUMBER)
        # This is the key change: we map by local citation NUMBER, not ref_id
        self.cell_local_refs: Dict[Tuple[int, int], Reference] = {}
        
        # Ordered list of unique references by first appearance
        self.global_order: List[Reference] = []
    
    def extract_references_from_cell(self, cell_index: int, markdown_text: str) -> Tuple[Set[str], Dict[str, Reference]]:
        """
        Extract both citations and definitions from a markdown cell.
        
        Args:
            cell_index: Index of the cell in the notebook
            markdown_text: The markdown source text
        
        Returns:
            Tuple of:
                - Set of ref_ids cited in this cell
                - Dict of ref_id -> Reference for definitions found
        """
        cited_refs = set()
        defined_refs = {}
        
        # Extract citations (references used in text)
        for match in self.CITATION_PATTERN.finditer(markdown_text):
            local_num = int(match.group(1))
            ref_id = match.group(2)
            cited_refs.add(ref_id)
        
        # Extract definitions (reference declarations)
        for match in self.DEFINITION_START_PATTERN.finditer(markdown_text):
            ref_id = match.group(1)  # e.g., "ref1"
            local_num = int(match.group(2))  # e.g., 1
            
            # Extract the full definition text
            # Get text from match start to next reference or end
            start_pos = match.end()
            remaining_text = markdown_text[start_pos:]
            
            # Find next reference definition or end of text
            next_match = self.DEFINITION_START_PATTERN.search(remaining_text)
            if next_match:
                definition_text = match.group(3) + remaining_text[:next_match.start()]
            else:
                definition_text = match.group(3) + remaining_text
            
            # Clean up the definition text
            definition_text = definition_text.strip()
            
            # Create Reference object
            ref = Reference(ref_id, local_num, definition_text, cell_index)
            defined_refs[ref_id] = ref
        
        return cited_refs, defined_refs
    
    def build_global_reference_map(self, notebook_cells: List) -> None:
        """
        Scan all markdown cells and build global reference mapping.
        
        The key insight: each cell has its own local numbering (ref1, ref2, ...),
        but these may refer to different actual references. We need to:
        1. Extract all reference definitions with their content
        2. Deduplicate by content to find unique references
        3. Build mapping from (cell_index, local_id) -> global_num
        
        Args:
            notebook_cells: List of notebook cells (nbformat cells or dicts)
        """
        # First pass: collect all reference definitions
        for cell_idx, cell in enumerate(notebook_cells):
            # Support both dict and object access
            cell_type = getattr(cell, 'cell_type', None) or cell.get('cell_type')
            if cell_type != 'markdown':
                continue
            
            # Get source
            source = getattr(cell, 'source', None) or cell.get('source', [])
            if isinstance(source, list):
                markdown_text = ''.join(source)
            else:
                markdown_text = source
            
            # Extract only definitions from this cell
            _, defined_refs = self.extract_references_from_cell(cell_idx, markdown_text)
            
            # Process each definition found in this cell
            for ref_id, ref in defined_refs.items():
                # Normalize for deduplication
                normalized = ref.normalize_for_dedup(ref.definition)
                
                # Check if this normalized definition already exists
                if normalized in self.unique_references:
                    # Reuse existing reference
                    existing_ref = self.unique_references[normalized]
                    # Map by LOCAL NUMBER (not ref_id) for robust citation lookup
                    self.cell_local_refs[(cell_idx, ref.local_num)] = existing_ref
                else:
                    # New unique reference
                    self.unique_references[normalized] = ref
                    self.global_order.append(ref)
                    # Map by LOCAL NUMBER (not ref_id)
                    self.cell_local_refs[(cell_idx, ref.local_num)] = ref
        
        # Assign global numbers by order of first appearance
        for global_num, ref in enumerate(self.global_order, start=1):
            ref.global_num = global_num
    
    def get_local_to_global_map(self, cell_index: int) -> Dict[int, int]:
        """
        Get mapping of local reference numbers to global numbers for a specific cell.
        
        Args:
            cell_index: Index of the cell
        
        Returns:
            Dict mapping local_num -> global_num
        """
        mapping = {}
        
        if cell_index not in self.cell_references:
            return mapping
        
        for ref_id in self.cell_references[cell_index]:
            if ref_id in self.references:
                ref = self.references[ref_id]
                mapping[ref.local_num] = ref.global_num
        
        return mapping
    
    def remove_reference_section(self, markdown_text: str) -> str:
        """
        Remove the local reference section from markdown text.
        
        Args:
            markdown_text: The markdown source text
        
        Returns:
            Text with reference section removed
        """
        # Find the reference section separator
        match = self.REFERENCE_SECTION_PATTERN.search(markdown_text)
        if not match:
            return markdown_text
        
        # Remove everything from the separator onwards
        return markdown_text[:match.start()].rstrip()
    
    def update_citations_in_text(self, cell_index: int, markdown_text: str) -> str:
        """
        Update citation numbers in markdown text to use global numbering.
        
        Args:
            cell_index: Index of the cell
            markdown_text: The markdown source text
        
        Returns:
            Updated markdown text with global reference numbers
        """
        def replace_citation(match):
            local_num = int(match.group(1))  # The [[X]] number
            # Ignore the ref_id from the link - it may be wrong in the source
            
            # Look up the reference using (cell_index, local_num)
            # This is robust: we match citation [[X]] with definition [X]
            key = (cell_index, local_num)
            if key not in self.cell_local_refs:
                # Keep original if no mapping found
                return match.group(0)
            
            ref = self.cell_local_refs[key]
            global_num = ref.global_num
            
            # Create new global ref_id
            global_ref_id = f"global_ref{global_num}"
            
            # Return updated citation
            return f"[[{global_num}]](#{global_ref_id})"
        
        return self.CITATION_PATTERN.sub(replace_citation, markdown_text)
    
    def remove_reference_section(self, markdown_text: str) -> str:
        """
        Remove the local reference section from markdown text.
        This removes everything from the separator or first reference definition onwards.
        Preserves PAGE_BREAK markers that appear before the references section.
        
        Args:
            markdown_text: The markdown source text
        
        Returns:
            Text with reference section removed, preserving PAGE_BREAK before refs
        """
        # Strategy 1: Look for explicit separator "---\n**Références :**"
        # This is the most reliable pattern
        match = self.REFERENCE_SECTION_PATTERN.search(markdown_text)
        if match:
            # Check if there's a PAGE_BREAK just before the separator
            before_separator = markdown_text[:match.start()]
            page_break_pattern = re.compile(r'(<!--\s*PAGE_BREAK\s*-->\s*)$')
            pb_match = page_break_pattern.search(before_separator)
            if pb_match:
                # Keep the PAGE_BREAK marker
                return before_separator.rstrip()
            else:
                # No PAGE_BREAK, just remove from separator
                return before_separator.rstrip()
        
        # Strategy 2: Look for "---" followed by reference definitions within a few lines
        # We need to check that --- is IMMEDIATELY before references (not just somewhere after)
        lines = markdown_text.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == '---':
                # Check the next few lines (up to 5) for reference pattern
                next_lines = lines[i:min(i+5, len(lines))]
                next_text = '\n'.join(next_lines)
                if self.DEFINITION_START_PATTERN.search(next_text):
                    # Check if there's a PAGE_BREAK before this ---
                    if i > 0 and '<!-- PAGE_BREAK -->' in lines[i-1]:
                        # Keep the PAGE_BREAK and everything before it
                        return '\n'.join(lines[:i]).rstrip()
                    else:
                        # This --- is immediately before references, remove from here
                        return '\n'.join(lines[:i]).rstrip()
        
        # Strategy 3: If no separator, find first reference definition and remove from there
        match = self.DEFINITION_START_PATTERN.search(markdown_text)
        if match:
            # Check for PAGE_BREAK just before the reference
            before_ref = markdown_text[:match.start()]
            if '<!-- PAGE_BREAK -->' in before_ref[-50:]:  # Check last 50 chars
                # Keep content up to and including PAGE_BREAK
                return before_ref.rstrip()
            else:
                return before_ref.rstrip()
        
        # No references found
        return markdown_text
    
    def process_markdown_cell(self, cell_index: int, cell) -> None:
        """
        Process a markdown cell: update citations and remove local references.
        
        Args:
            cell_index: Index of the cell
            cell: The notebook cell object (will be modified in place)
        """
        # Support both dict and object access
        cell_type = getattr(cell, 'cell_type', None) or cell.get('cell_type')
        if cell_type != 'markdown':
            return
        
        # Get source as string
        source = getattr(cell, 'source', None) or cell.get('source', [])
        if isinstance(source, list):
            markdown_text = ''.join(source)
        else:
            markdown_text = source
        
        # Step 1: Update citation numbers to global
        markdown_text = self.update_citations_in_text(cell_index, markdown_text)
        
        # Step 2: Remove local reference section
        markdown_text = self.remove_reference_section(markdown_text)
        
        # Update cell source
        if hasattr(cell, 'source'):
            cell.source = markdown_text
        else:
            cell['source'] = markdown_text
    
    def generate_references_section(self) -> str:
        """
        Generate the final consolidated references section.
        
        Returns:
            Markdown text for the references section
        """
        if not self.global_order:
            return ""
        
        lines = [
            "\n\n",
            "---\n",
            "\n",
            "### Références\n",
            "\n"
        ]
        
        for ref in self.global_order:
            global_ref_id = f"global_ref{ref.global_num}"
            # Don't clean PAGE_BREAK from definitions - just use as-is
            lines.append(
                f'<a id="{global_ref_id}"></a>**[{ref.global_num}]** {ref.definition}\n\n'
            )
        
        return ''.join(lines)
    
    def process_notebook(self, notebook) -> None:
        """
        Process entire notebook: extract, remap, and consolidate references.
        
        This modifies the notebook in place:
        - Updates citation numbers in markdown cells
        - Removes local reference sections
        - Adds final references cell (if references exist)
        
        Args:
            notebook: nbformat notebook object
        """
        # Support both dict and object access for cells
        cells = getattr(notebook, 'cells', None) or notebook.get('cells', [])
        
        # Step 1: Build global reference map
        self.build_global_reference_map(cells)
        
        # Step 2: Process all markdown cells
        for cell_idx, cell in enumerate(cells):
            cell_type = getattr(cell, 'cell_type', None) or cell.get('cell_type')
            if cell_type == 'markdown':
                self.process_markdown_cell(cell_idx, cell)
        
        # Step 3: Add final references section (if any references exist)
        if self.global_order:
            references_markdown = self.generate_references_section()
            
            # Import nbformat to create proper cell
            try:
                import nbformat
                references_cell = nbformat.v4.new_markdown_cell(references_markdown)
                references_cell.metadata['references_section'] = True
            except ImportError:
                # Fallback to dict if nbformat not available
                references_cell = {
                    'cell_type': 'markdown',
                    'metadata': {'references_section': True},
                    'source': references_markdown
                }
            
            # Add to end of notebook
            cells.append(references_cell)
