# Proposal: Web Page Display for Job Listings

**Date:** 2026-01-03  
**Phase:** Output - Generate Webpage  
**Status:** Proposed

## Overview

Design and implement a web-based interface to display the processed job listings from the data pipeline. The webpage should provide an intuitive, searchable, and filterable interface for users to browse academic economics job opportunities.

## Objectives

1. Create a user-friendly interface to display 200+ job listings
2. Implement filtering and search functionality
3. Provide responsive design for desktop and mobile devices
4. Enable easy navigation and job discovery
5. Display all relevant job information in a structured format

## Data Source

- **Input:** `data/processed/jobs.json` (211 unique listings after deduplication)
- **Format:** JSON with structured fields (title, institution, department, location, deadline, etc.)
- **Update Frequency:** Daily (when scraping pipeline runs)

## Proposed Design

### 1. Technology Stack

**Option A: Static Site (Recommended for MVP)**
- **HTML + CSS + JavaScript** (vanilla or lightweight framework)
- **Advantages:**
  - No server required (can host on GitHub Pages, Netlify, etc.)
  - Fast loading
  - Simple deployment
  - Direct JSON consumption
- **Tools:**
  - Jinja2 templates (already in dependencies)
  - Bootstrap or Tailwind CSS for styling
  - JavaScript for client-side filtering/search

**Option B: Dynamic Web Application**
- **Flask/FastAPI** backend + **HTML/CSS/JS** frontend
- **Advantages:**
  - More control over data processing
  - Can add API endpoints
  - Server-side rendering options
- **Disadvantages:**
  - Requires server hosting
  - More complex deployment

**Recommendation:** Start with Option A (static site) for simplicity and scalability.

### 2. Page Structure

```
├── index.html (main listing page)
├── css/
│   ├── styles.css (custom styles)
│   └── [framework.css] (Bootstrap/Tailwind)
├── js/
│   ├── app.js (main application logic)
│   ├── filters.js (filtering functionality)
│   └── search.js (search functionality)
├── data/
│   └── jobs.json (symlink or copy from processed/)
└── assets/
    └── images/ (logos, icons)
```

### 3. User Interface Components

#### A. Header Section
- **Title:** "Economics Faculty Job Openings"
- **Subtitle:** "Daily updated aggregator of academic positions"
- **Last Updated:** Display timestamp from JSON metadata
- **Statistics:** Total listings, new listings, active listings

#### B. Filter Sidebar (Left)
**Filters:**
1. **Location**
   - Region dropdown (US, UK, Canada, China, Australia, Other)
   - Country multi-select
   - State/Province (for US/Canada)

2. **Job Type**
   - Tenure-track
   - Visiting
   - Postdoc
   - Lecturer
   - Other

3. **Institution Type**
   - University
   - Research Institute
   - Think Tank
   - Job Portal

4. **Department Category**
   - Economics
   - Management
   - Marketing
   - Other

5. **Deadline**
   - All listings
   - Within 1 month
   - Within 3 months
   - Within 6 months
   - Custom date range

6. **Status**
   - Active only
   - All listings (including expired)

#### C. Search Bar (Top)
- **Full-text search** across:
  - Job title
  - Institution name
  - Department
  - Description
  - Requirements
- **Search tips tooltip**
- **Clear search button**

#### D. Sorting Options
- Relevance (when searching)
- Deadline (earliest first)
- Posted date (newest first)
- Institution name (A-Z)
- Location (grouped by region/country)

#### E. Job Listing Cards (Main Content)

**Card Layout:**
```
┌─────────────────────────────────────────────┐
│ [NEW] Job Title                      [SAVE] │
│ Institution Name • Department               │
│ 📍 Location          📅 Deadline: MM/DD/YYYY│
│                                             │
│ Brief description preview (2-3 lines)...   │
│                                             │
│ 🏷️ Tags: Tenure-track, Economics          │
│                                             │
│ [View Details] [Apply ↗]                   │
└─────────────────────────────────────────────┘
```

**Card Information:**
- **Visual Indicators:**
  - [NEW] badge for recent listings (is_new: true)
  - Color coding by deadline urgency (red <1 month, yellow <3 months)
  - Institution type icon
  
- **Primary Info:**
  - Job title (clickable to expand)
  - Institution name
  - Department
  - Location (city, state, country)
  - Deadline with countdown
  
- **Secondary Info (collapsed):**
  - Full description
  - Requirements
  - Specializations
  - Materials required
  - Salary range (if available)
  - Start date
  - Contact information
  
- **Actions:**
  - View Details (expand/modal)
  - Apply (external link)
  - Save/Bookmark (localStorage)

#### F. Pagination
- Show 20 listings per page (configurable)
- Page numbers with prev/next
- Jump to page input
- Results count: "Showing 1-20 of 211 listings"

### 4. Responsive Design

**Desktop (>1024px):**
- 3-column layout: Filters (left) | Listings (center) | Info panel (right, optional)
- Cards in 1-2 column grid

**Tablet (768px - 1024px):**
- Collapsible filter sidebar
- Single column cards
- Sticky header with filters button

**Mobile (<768px):**
- Hamburger menu for filters
- Single column layout
- Simplified cards (less detail)
- Bottom sticky filter/sort buttons

### 5. Features & Functionality

#### Essential Features (MVP)
1. ✅ Display all job listings from JSON
2. ✅ Filter by location, job type, institution type, department
3. ✅ Search functionality
4. ✅ Sort by deadline, date posted, institution
5. ✅ Responsive design
6. ✅ External links to application pages

#### Enhanced Features (Phase 2)
1. 📌 Save/bookmark listings (localStorage)
2. 🔔 Email notifications for new listings (requires backend)
3. 📊 Statistics dashboard (charts showing trends)
4. 🔗 Share individual listing (copy link)
5. 🌓 Dark mode toggle
6. 📱 PWA (Progressive Web App) for offline access
7. 🔄 Auto-refresh when new data available

#### Advanced Features (Future)
1. 🤖 AI-powered job matching based on user profile
2. 👤 User accounts and saved searches
3. 📈 Historical data and trends
4. 🗺️ Map view of job locations
5. 📧 Application tracking system

### 6. Data Integration

**Static Approach:**
```javascript
// Fetch jobs data
fetch('data/jobs.json')
  .then(response => response.json())
  .then(data => {
    const listings = data.listings;
    const metadata = data.metadata;
    renderListings(listings);
    updateStats(metadata);
  });
```

**Data Refresh:**
- Manual page reload
- Auto-reload every N minutes (via setInterval)
- Service worker for background updates (PWA)

### 7. Performance Considerations

1. **Load Time:**
   - Gzip JSON file
   - Lazy load images
   - Defer non-critical JS
   - CSS minification

2. **Rendering:**
   - Virtual scrolling for large lists
   - Debounce search input
   - Throttle filter updates
   - Use CSS transforms for animations

3. **Data Size:**
   - Current: 211 listings (~500KB JSON)
   - Expected growth: ~1000 listings (~2MB JSON)
   - Solution: Pagination + lazy loading

### 8. Accessibility

1. **ARIA labels** for screen readers
2. **Keyboard navigation** support
3. **Color contrast** meeting WCAG AA standards
4. **Focus indicators** for interactive elements
5. **Alt text** for all images
6. **Semantic HTML** structure

### 9. SEO Optimization

1. **Meta tags:** Title, description, keywords
2. **Open Graph** tags for social sharing
3. **Schema.org** JobPosting markup
4. **Sitemap** generation
5. **robots.txt** configuration

### 10. Deployment

**Static Site Hosting Options:**
1. **GitHub Pages** (free, easy deployment from repo)
2. **Netlify** (free tier, auto-deploy on push)
3. **Vercel** (free tier, optimized for static sites)
4. **AWS S3 + CloudFront** (scalable, requires setup)

**Deployment Workflow:**
```bash
# Option 1: Manual copy
cp data/processed/jobs.json static/data/

# Option 2: Build script
python scripts/generator/build_site.py

# Option 3: GitHub Actions (automated)
# On push to main: run pipeline → update JSON → deploy
```

## Implementation Plan

### Phase 1: Basic Display (Week 1)
1. Create HTML template with Jinja2
2. Implement basic CSS styling (Bootstrap)
3. Load and display jobs from JSON
4. Basic card layout
5. Deploy to GitHub Pages

### Phase 2: Filtering & Search (Week 2)
1. Implement filter sidebar
2. Add search functionality
3. Implement sorting options
4. Add pagination
5. Refine UI/UX

### Phase 3: Polish & Features (Week 3)
1. Responsive design optimization
2. Add save/bookmark feature
3. Implement statistics display
4. Performance optimization
5. Accessibility audit
6. Cross-browser testing

### Phase 4: Advanced Features (Future)
1. Dark mode
2. PWA setup
3. Analytics integration
4. User feedback system

## File Structure in Project

```
static/
├── index.html              # Main page
├── css/
│   ├── styles.css         # Custom styles
│   └── bootstrap.min.css  # Framework (optional)
├── js/
│   ├── app.js            # Main application
│   ├── filters.js        # Filter logic
│   ├── search.js         # Search logic
│   └── utils.js          # Helper functions
├── data/
│   └── jobs.json         # Symlink to processed/jobs.json
└── images/
    └── [icons, logos]

templates/
└── index.html.jinja      # Jinja2 template (if using generator)

scripts/generator/
├── __init__.py
├── build_site.py         # Build script
└── template_renderer.py  # Jinja2 rendering
```

## Success Metrics

1. **Performance:**
   - Page load time < 2 seconds
   - Time to interactive < 3 seconds

2. **Usability:**
   - User can find relevant jobs in < 30 seconds
   - Mobile-friendly (Google PageSpeed > 90)

3. **Adoption:**
   - Track page views
   - Monitor search queries
   - Collect user feedback

## Risks & Mitigation

1. **Risk:** Large JSON file size (as listings grow)
   - **Mitigation:** Implement pagination, lazy loading, or API endpoint

2. **Risk:** Stale data if pipeline fails
   - **Mitigation:** Display last updated timestamp, implement health check

3. **Risk:** Poor performance on mobile
   - **Mitigation:** Progressive enhancement, mobile-first design

4. **Risk:** Browser compatibility issues
   - **Mitigation:** Use polyfills, test on multiple browsers

## Next Steps

1. ✅ Review and approve proposal
2. Create generator script structure
3. Design HTML template with Jinja2
4. Implement basic styling
5. Test with current jobs.json
6. Deploy MVP to GitHub Pages

## Questions for Decision

1. Which CSS framework? (Bootstrap vs Tailwind vs custom)
2. Static site or dynamic application?
3. Hosting preference? (GitHub Pages vs Netlify vs other)
4. Additional features for MVP?
5. Design preferences (colors, layout, branding)?
