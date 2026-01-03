import re

with open('static/index.html', encoding='utf-8') as f:
    lines = f.readlines()

# Find lines with data-specializations
spec_lines = [l for l in lines if 'data-specializations=' in l]
print(f"Total job cards with specializations attribute: {len(spec_lines)}")

# Check actual values
empty = 0
valid_json = 0
invalid = []

for line in spec_lines:
    # Extract the value between quotes
    match = re.search(r'data-specializations="([^"]*)"', line)
    if match:
        value = match.group(1)
        if value == '[]':
            empty += 1
        elif value.startswith('[') and value.endswith(']'):
            valid_json += 1
        else:
            invalid.append(value)

print(f"\nResults:")
print(f"  Empty arrays: {empty}")
print(f"  Valid JSON: {valid_json}")
print(f"  Invalid: {len(invalid)}")

if invalid:
    print(f"\nExamples of invalid values:")
    for v in invalid[:5]:
        print(f"  '{v}' (length: {len(v)})")
