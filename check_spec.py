import json

with open('data/processed/jobs.json', encoding='utf-8') as f:
    data = json.load(f)

# Check jobs without specializations
no_spec = [j for j in data if not j.get('specializations')]
with_spec = [j for j in data if j.get('specializations')]

print(f"Total jobs: {len(data)}")
print(f"Jobs with specializations: {len(with_spec)}")
print(f"Jobs without specializations: {len(no_spec)}")
print()

print("Sample of jobs WITHOUT specializations:")
for j in no_spec[:3]:
    print(f"  ID: {j.get('id')}")
    print(f"  Title: {j.get('title')}")
    print(f"  Specializations field: {repr(j.get('specializations'))}")
    print()

print("Sample of jobs WITH specializations:")
for j in with_spec[:3]:
    print(f"  ID: {j.get('id')}")
    print(f"  Title: {j.get('title')}")
    print(f"  Specializations field: {repr(j.get('specializations'))}")
    print()
