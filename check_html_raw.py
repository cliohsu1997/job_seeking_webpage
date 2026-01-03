with open('static/index.html', encoding='utf-8') as f:
    content = f.read()

# Find first few data-specializations
idx = 0
count = 0
while count < 5:
    idx = content.find('data-specializations', idx)
    if idx == -1:
        break
    # Get 300 chars from this point
    section = content[idx:idx+300]
    print(f"\n=== Match {count+1} ===")
    print(section)
    print("---")
    idx += 20
    count += 1
