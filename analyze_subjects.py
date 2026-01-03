import json

with open('data/processed/jobs.json', encoding='utf-8') as f:
    data = json.load(f)

listings = data['listings']
print(f'Total listings: {len(listings)}')

# Department category distribution
dept_cats = {}
for job in listings:
    cat = job.get('department_category', 'None')
    dept_cats[cat] = dept_cats.get(cat, 0) + 1

print('\n=== Department Category Distribution ===')
for cat, count in sorted(dept_cats.items(), key=lambda x: -x[1]):
    percentage = (count / len(listings)) * 100
    print(f'  {cat}: {count} ({percentage:.1f}%)')

# Specializations coverage
spec_count = sum(1 for job in listings if job.get('specializations'))
print(f'\n=== Specializations Coverage ===')
print(f'Jobs with specializations: {spec_count}/{len(listings)} ({(spec_count/len(listings)*100):.1f}%)')

# Sample jobs with different categories
print('\n=== Sample Jobs by Category ===')
for cat in ['Economics', 'Management', 'Marketing', 'Other']:
    jobs = [j for j in listings if j.get('department_category') == cat]
    if jobs:
        job = jobs[0]
        print(f'\n{cat}:')
        print(f'  Title: {job.get("title", "N/A")}')
        print(f'  Dept: {job.get("department", "N/A")}')
        print(f'  Specializations: {job.get("specializations", [])}')
