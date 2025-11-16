"""Table of contents and cover page generation."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple


def extract_headings(html: str, max_depth: int = 3) -> List[Tuple[int, str, str]]:
    """Extract headings from HTML.
    
    Returns:
        List of (level, text, id) tuples
    """
    headings = []
    # Match h1-h6 tags with optional id
    pattern = r'<h([1-6])(?:[^>]*id="([^"]*)")?[^>]*>(.*?)</h\1>'
    
    for match in re.finditer(pattern, html, re.DOTALL):
        level = int(match.group(1))
        if level > max_depth:
            continue
        
        heading_id = match.group(2) or f"heading-{len(headings)}"
        # Clean HTML tags from text
        text = re.sub(r'<[^>]+>', '', match.group(3))
        text = text.strip()
        # Remove pilcrow (¶) and other anchor symbols
        text = text.replace('¶', '').strip()
        
        headings.append((level, text, heading_id))
    
    return headings


def generate_toc_html(headings: List[Tuple[int, str, str]], config: Dict[str, Any]) -> str:
    """Generate table of contents HTML."""
    if not headings:
        return ""
    
    toc_title = config.get("toc_title", "Table des matières")
    
    html = f'''
<div class="toc-page">
    <h1 class="toc-title">{toc_title}</h1>
    <nav class="toc">
'''
    
    current_level = 0
    for level, text, heading_id in headings:
        # Open/close nested lists as needed
        while current_level < level:
            html += '        <ol class="toc-list">\n'
            current_level += 1
        while current_level > level:
            html += '        </ol>\n'
            current_level -= 1
        
        html += f'            <li class="toc-item toc-level-{level}">'
        html += f'<a href="#{heading_id}" class="toc-link">{text}</a></li>\n'
    
    # Close remaining lists
    while current_level > 0:
        html += '        </ol>\n'
        current_level -= 1
    
    html += '''    </nav>
</div>
'''
    
    return html


def generate_cover_html(config: Dict[str, Any]) -> str:
    """Generate cover page HTML."""
    title = config.get("cover_title", "")
    subtitle = config.get("cover_subtitle", "")
    authors = config.get("cover_authors", [])
    # Support legacy single author field
    if not authors and config.get("cover_author"):
        authors = [config.get("cover_author")]
    institution = config.get("cover_institution", "")
    subject = config.get("cover_subject", "")
    date = config.get("cover_date", "auto")
    logo = config.get("cover_logo", "")
    quote = config.get("cover_quote", "")
    
    if date == "auto":
        date = datetime.now().strftime("%d %B %Y")
    
    html = '<div class="cover-page">\n'
    
    # Top section: institution and/or subject
    has_header = institution or subject
    if has_header:
        html += '    <div class="cover-header">\n'
        if institution:
            html += f'        <div class="cover-institution-top">{institution}</div>\n'
        if subject:
            html += f'        <div class="cover-subject">{subject}</div>\n'
        html += '    </div>\n'
    
    # Middle section: logo and title
    html += '    <div class="cover-main">\n'
    
    if logo:
        html += f'        <div class="cover-logo"><img src="{logo}" alt="Logo" /></div>\n'
    
    if title:
        html += f'        <h1 class="cover-title">{title}</h1>\n'
    
    if subtitle:
        html += f'        <h2 class="cover-subtitle">{subtitle}</h2>\n'
    
    html += '    </div>\n'
    
    # Bottom section: author and date
    has_footer = authors or date or quote
    if has_footer:
        html += '    <div class="cover-footer">\n'
        
        if authors:
            if len(authors) == 1:
                html += f'        <div class="cover-author-single">par {authors[0]}</div>\n'
            else:
                html += '        <div class="cover-authors-box">\n'
                html += '            <div class="cover-authors-title">Auteurs</div>\n'
                html += '            <ul class="cover-authors-list">\n'
                for author in authors:
                    html += f'                <li>{author}</li>\n'
                html += '            </ul>\n'
                html += '        </div>\n'
        
        if date:
            html += f'        <div class="cover-date">{date}</div>\n'
        
        if quote:
            html += f'        <div class="cover-quote">{quote}</div>\n'
        
        html += '    </div>\n'
    
    html += '</div>\n'
    
    return html


def add_heading_ids(html: str) -> str:
    """Add IDs to headings that don't have them for TOC linking."""
    def replace_heading(match):
        tag = match.group(1)
        attrs = match.group(2) or ""
        content = match.group(3)
        
        # Check if already has ID
        if 'id=' in attrs:
            return match.group(0)
        
        # Generate ID from content
        heading_id = re.sub(r'[^a-z0-9]+', '-', content.lower())
        heading_id = heading_id.strip('-')
        
        return f'<h{tag} {attrs} id="{heading_id}">{content}</h{tag}>'
    
    pattern = r'<h([1-6])([^>]*)>(.*?)</h\1>'
    return re.sub(pattern, replace_heading, html, flags=re.DOTALL)
