"""LaTeX to SVG converter for math equations."""

from __future__ import annotations

import re
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any


# Cache pour les équations déjà converties
_svg_cache: Dict[str, str] = {}


def latex_to_svg(latex_code: str, display_mode: bool = False) -> str:
    """
    Convert LaTeX math to SVG using latex and dvisvgm.
    
    Args:
        latex_code: The LaTeX math code (without $ delimiters)
        display_mode: True for display math ($$), False for inline ($)
    
    Returns:
        SVG code as string, or original LaTeX if conversion fails
    """
    # Generate cache key
    cache_key = hashlib.md5(f"{latex_code}_{display_mode}".encode()).hexdigest()
    
    if cache_key in _svg_cache:
        return _svg_cache[cache_key]
    
    try:
        # For now, return a placeholder that will be styled
        # In production, you would use mathjax-node-cli or similar
        style = "display: block; text-align: center;" if display_mode else "display: inline;"
        svg_html = f'<span class="math-fallback" style="{style}">${latex_code}$</span>'
        _svg_cache[cache_key] = svg_html
        return svg_html
    except Exception as e:
        # Return original on error
        return f"${latex_code}$" if not display_mode else f"$${latex_code}$$"


def process_latex_in_html(html: str) -> str:
    """
    Process HTML to convert LaTeX math to SVG.
    
    This function finds LaTeX patterns and converts them to SVG.
    For now, it wraps them in spans for CSS styling.
    """
    # For inline math: $...$
    inline_pattern = r'\$([^\$\n]+?)\$'
    html = re.sub(inline_pattern, lambda m: latex_to_svg(m.group(1), False), html)
    
    # For display math: $$...$$
    display_pattern = r'\$\$([^\$]+?)\$\$'
    html = re.sub(display_pattern, lambda m: latex_to_svg(m.group(1), True), html, flags=re.DOTALL)
    
    return html
