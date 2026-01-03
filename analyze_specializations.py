import json
from collections import Counter

with open('data/processed/jobs.json', encoding='utf-8') as f:
    data = json.load(f)

listings = data['listings']

# Collect all unique specializations
all_specs = []
for job in listings:
    specs = job.get('specializations', [])
    if specs:
        all_specs.extend(specs)

# Count specializations
spec_counts = Counter(all_specs)

print(f'Total jobs: {len(listings)}')
print(f'Jobs with specializations: {sum(1 for j in listings if j.get("specializations"))} ({sum(1 for j in listings if j.get("specializations"))/len(listings)*100:.1f}%)')
print(f'\n=== Top Specializations ===')
for spec, count in spec_counts.most_common(20):
    print(f'{spec}: {count}')
