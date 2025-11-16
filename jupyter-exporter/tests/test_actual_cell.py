"""Test removal on the actual last cell content."""

import re

REFERENCE_SECTION_PATTERN = re.compile(
    r'^\s*---\s*\n\s*\*\*Références\s*:\*\*\s*\n',
    re.MULTILINE
)

DEFINITION_START_PATTERN = re.compile(r'<a\s+id="(ref\d+)"\s*></a>\[(\d+)\]\s*(.+)', re.MULTILINE)

# The actual content from the last cell
test_text = """---

### Ouvertures

Ce travail ouvre la voie à plusieurs approfondissements essentiels :

* **Le Paradigme Monte-Carlo :** Il serait pertinent de s'attaquer au paradigme Monte-Carlo (résultat approximatif, temps borné). L'analyse de l'**algorithme de Karger** [[1]](#ref1) pour la coupe minimale, serait un cas d'étude fascinant, nécessitant de calculer non pas une espérance de coût, mais une probabilité de succès (ex: $P(succ \ge 2/n^2)$) et les techniques d'**amplification** (répétition) nécessaires pour la rendre fiable.

---
**Références :**

<a id="ref1"></a>[1] Mitzenmacher, M., & Upfal, E. (2005). *Probability and Computing*. Cambridge University Press."""

print("Original text length:", len(test_text))
print("\n=== Testing Strategy 1: REFERENCE_SECTION_PATTERN ===")
match = REFERENCE_SECTION_PATTERN.search(test_text)
if match:
    print(f"✓ Match found at {match.start()}-{match.end()}")
    print(f"Matched text: {repr(test_text[match.start():match.end()])}")
    cleaned = test_text[:match.start()].rstrip()
    print(f"Cleaned length: {len(cleaned)}")
else:
    print("✗ No match")

print("\n=== Testing Strategy 2 IMPROVED: Looking for --- within 5 lines before references ===")
lines = test_text.split('\n')
found_separator = False
for i, line in enumerate(lines):
    if line.strip() == '---':
        print(f"Found --- at line {i}: {repr(line)}")
        # Check only the next 5 lines
        next_lines = lines[i:min(i+5, len(lines))]
        next_text = '\n'.join(next_lines)
        if DEFINITION_START_PATTERN.search(next_text):
            print(f"  ✓ This --- is IMMEDIATELY followed by reference definitions")
            print(f"  Would cut at line {i}")
            cleaned = '\n'.join(lines[:i]).rstrip()
            print(f"  Cleaned length: {len(cleaned)}")
            print(f"  Cleaned text (last 100 chars): {cleaned[-100:]}")
            found_separator = True
            break
        else:
            print(f"  ✗ This --- is NOT immediately followed by references (within 5 lines)")

if not found_separator:
    print("✗ No --- found immediately before references")

print("\n=== Testing Strategy 3: DEFINITION_START_PATTERN ===")
match = DEFINITION_START_PATTERN.search(test_text)
if match:
    print(f"✓ Match found at {match.start()}-{match.end()}")
    print(f"Matched text: {repr(test_text[match.start():match.start()+50])}")
    cleaned = test_text[:match.start()].rstrip()
    print(f"Cleaned length: {len(cleaned)}")
    print(f"\nCleaned text (last 200 chars):")
    print(cleaned[-200:])
else:
    print("✗ No match")
