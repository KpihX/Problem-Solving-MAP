"""Simple test of reference removal."""

import re

REFERENCE_SECTION_PATTERN = re.compile(
    r'^\s*---\s*\n\s*\*\*Références\s*:\*\*\s*\n',
    re.MULTILINE
)

DEFINITION_START_PATTERN = re.compile(r'<a\s+id="(ref\d+)"\s*></a>\[(\d+)\]\s*(.+)', re.MULTILINE)

test_text = """Texte avant les références.

---
**Références :**

<a id="ref1"></a>[1] Mitzenmacher, M., & Upfal, E. (2005). *Probability and Computing*. Cambridge University Press.

<!-- PAGE_BREAK -->"""

print("Original text:")
print(test_text)
print("\n" + "="*60 + "\n")

# Test separator pattern
match = REFERENCE_SECTION_PATTERN.search(test_text)
if match:
    print(f"Separator found at position {match.start()}-{match.end()}")
    cleaned = test_text[:match.start()].rstrip()
    print(f"\nCleaned text:\n{cleaned}")
else:
    print("Separator NOT found!")
    
    # Try definition pattern
    match = DEFINITION_START_PATTERN.search(test_text)
    if match:
        print(f"\nDefinition found at position {match.start()}-{match.end()}")
        cleaned = test_text[:match.start()].rstrip()
        print(f"\nCleaned text:\n{cleaned}")
    else:
        print("Definition NOT found either!")
