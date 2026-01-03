import re

with open('static/index.html', encoding='utf-8') as f:
    content = f.read()

# Find all data-specializations attributes 
# Match the full attribute value more carefully
pattern = r'data-specializations="([^"]*(?:"[^"]*"[^"]*)*)"'
matches = re.findall(pattern, content)

print(f"Total matches: {len(matches)}")

# Filter to check different types
empty_arrays = [m for m in matches if m == '[]']
incomplete = [m for m in matches if m == '[']
unclosed = [m for m in matches if m.startswith('[') and not m.endswith(']')]
valid = [m for m in matches if m.startswith('[') and m.endswith(']') and len(m) > 2]

print(f"\nStatistics:")
print(f"  Empty arrays []: {len(empty_arrays)}")
print(f"  Incomplete [...: {len(incomplete)}")
print(f"  Unclosed arrays: {len(unclosed)}")
print(f"  Valid arrays: {len(valid)}")

print(f"\nSamples of invalid:")
for m in matches[:10]:
    if m == '[':
        print(f"  INCOMPLETE: '{m}'")
    elif m == '[]':
        print(f"  EMPTY: '{m}'")
    else:
        print(f"  OK: {m[:80]}...")


