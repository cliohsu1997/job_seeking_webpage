#!/usr/bin/env python3
"""Quick test of AEA scraper fixes"""

import sys
from pathlib import Path

sys.path.insert(0, 'scripts/scraper')
from aea_scraper import AEAScraper

scraper = AEAScraper()
html_path = Path('data/raw/aea/listings.html')

if html_path.exists():
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    listings = scraper.parse(html)
    print(f'Successfully parsed {len(listings)} listings')
    
    if listings:
        first = listings[0]
        print(f'\nFirst listing:')
        print(f'  Title: {first.get("title")}')
        print(f'  Institution: {first.get("institution")}')
        print(f'  Institution Type: {first.get("institution_type")}')
        print(f'  Department: {first.get("department")}')
        print(f'  Department Category: {first.get("department_category")}')
        print(f'  Location: {first.get("location")}')
        print(f'  Deadline: {first.get("deadline")}')
        print(f'  Application Link: {first.get("application_link")}')
        
        # Check if required fields are present
        required_fields = ['institution', 'institution_type', 'department', 'department_category', 'location']
        missing = [f for f in required_fields if not first.get(f)]
        if missing:
            print(f'\nMissing fields: {missing}')
        else:
            print(f'\nAll required fields present!')
else:
    print('HTML file not found')
