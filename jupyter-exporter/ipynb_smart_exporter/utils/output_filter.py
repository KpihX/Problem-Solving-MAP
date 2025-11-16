"""Output filtering for warnings and errors."""

from __future__ import annotations

import re


def filter_output_text(
    text: str | list[str],
    hide_warnings: bool = True,
    hide_errors: bool = False,
    warning_patterns: list[str] = None
) -> str | list[str]:
    """Filter warnings and errors from output text.
    
    Args:
        text: Output text or list of text lines
        hide_warnings: Whether to hide warnings
        hide_errors: Whether to hide errors
        warning_patterns: List of warning patterns to match
    
    Returns:
        Filtered text in same format as input
    """
    if not text or not hide_warnings:
        return text
    
    warning_patterns = warning_patterns or []
    is_list = isinstance(text, list)
    lines = text if is_list else text.split('\n')
    
    filtered_lines = []
    skip_block = False
    
    for line in lines:
        # Check for warning/error blocks
        should_hide = False
        for pattern in warning_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                should_hide = True
                break
        
        if hide_errors and re.search(r"error|exception|traceback", line, re.IGNORECASE):
            should_hide = True
        
        if should_hide:
            skip_block = True
            continue
        
        # Skip continuation lines of warning blocks
        if skip_block:
            # Check if line is indented (continuation)
            if line and (line[0].isspace() or line.startswith('  ')):
                continue
            else:
                skip_block = False
        
        filtered_lines.append(line)
    
    return filtered_lines if is_list else '\n'.join(filtered_lines)
