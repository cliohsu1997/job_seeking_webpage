# To-Do List: Phase 3 - Export (Output Generation)

**Date Created**: 2026-01-03  
**Phase**: Export - Generate Webpage  
**Status**: In Progress  
**Objective**: Create static webpage to display processed job listings with filtering, search, and responsive design

---

## Overview

Generate a user-friendly static website to display the 211 processed job listings from `data/processed/jobs.json`. The site will use HTML + CSS + JavaScript with Jinja2 templates for static generation, deployed to GitHub Pages.

---

## Phase 3A: Setup & Structure

### Task 1: Create Generator Script Structure
**Status**: ⏸️ Pending  
**Estimated Time**: 30 minutes

**Subtasks**:
- [ ] Create `scripts/generator/__init__.py`
- [ ] Create `scripts/generator/build_site.py` skeleton
- [ ] Create `scripts/generator/template_renderer.py` skeleton
- [ ] Add imports and basic structure

**Acceptance Criteria**:
- Generator module is importable
- Basic structure is in place for next steps

---

## Phase 3B: Template Design

### Task 2: Design HTML Template with Jinja2
**Status**: ⏸️ Pending  
**Estimated Time**: 2-3 hours

**Subtasks**:
- [ ] Create `templates/index.html.jinja`
- [ ] Implement header section (title, subtitle, statistics)
- [ ] Implement filter sidebar (location, job type, institution, department, deadline)
- [ ] Implement search bar (with sorting options)
- [ ] Implement job listing cards layout
  - [ ] Card header (title, institution, tags)
  - [ ] Card body (location, deadline, description preview)
  - [ ] Card footer (view details, apply buttons)
- [ ] Implement pagination component
- [ ] Add responsive grid structure
- [ ] Add placeholders for JavaScript functionality

**Acceptance Criteria**:
- Template renders with sample data
- All UI components are present
- Template uses Jinja2 variables for dynamic content
- Responsive layout structure in place

**Reference**:
- See proposal: `conversation_cursor/dates/2026-01-03/create-webpage-display-proposal.md` (Section 3: User Interface Components)

---

## Phase 3C: Styling

### Task 3: Implement Basic CSS Styling
**Status**: ⏸️ Pending  
**Estimated Time**: 2-3 hours

**Subtasks**:
- [ ] Create `static/css/styles.css`
- [ ] Choose CSS framework (Bootstrap vs Tailwind vs custom)
- [ ] Implement header styling
- [ ] Implement filter sidebar styling
  - [ ] Dropdowns and multi-selects
  - [ ] Checkboxes and radio buttons
  - [ ] Responsive collapse/expand
- [ ] Implement search bar and sorting styling
- [ ] Implement job card styling
  - [ ] Card layout (grid/flexbox)
  - [ ] Typography and spacing
  - [ ] Hover effects
  - [ ] Badge/tag styling
  - [ ] Visual indicators (NEW badge, deadline urgency colors)
- [ ] Implement pagination styling
- [ ] Implement responsive breakpoints
  - [ ] Desktop (>1024px): 3-column layout
  - [ ] Tablet (768px-1024px): collapsible sidebar
  - [ ] Mobile (<768px): hamburger menu, single column
- [ ] Add loading states and animations

**Acceptance Criteria**:
- All components are styled consistently
- Responsive design works across devices
- Visual hierarchy is clear
- Colors, fonts, and spacing follow design system
- Accessibility: good color contrast (WCAG AA)

**Design Decisions Needed**:
- CSS framework choice
- Color scheme
- Typography
- Branding/logo (if any)

---

## Phase 3D: JavaScript Functionality

### Task 4: Implement JavaScript Functionality
**Status**: ⏸️ Pending  
**Estimated Time**: 3-4 hours

**Subtasks**:

**4.1: Core Application Logic** (`static/js/app.js`)
- [ ] Load jobs.json data
- [ ] Parse and store listings
- [ ] Initialize application state
- [ ] Render initial listings (first 20)
- [ ] Update statistics (total, new, active)
- [ ] Set up event listeners

**4.2: Filtering Logic** (`static/js/filters.js`)
- [ ] Implement filter by location (region, country, state)
- [ ] Implement filter by job type
- [ ] Implement filter by institution type
- [ ] Implement filter by department category
- [ ] Implement filter by deadline (range selection)
- [ ] Implement filter by status (active/all)
- [ ] Implement multi-filter combination (AND logic)
- [ ] Update results count on filter change
- [ ] Add "Clear Filters" functionality

**4.3: Search Logic** (`static/js/search.js`)
- [ ] Implement full-text search across fields:
  - [ ] Title
  - [ ] Institution
  - [ ] Department
  - [ ] Description
  - [ ] Requirements
- [ ] Debounce search input (wait 300ms after typing stops)
- [ ] Highlight search matches (optional)
- [ ] Combine search with filters
- [ ] Add search tips tooltip

**4.4: Sorting Logic** (`static/js/app.js` or separate module)
- [ ] Implement sort by relevance (when searching)
- [ ] Implement sort by deadline (earliest first)
- [ ] Implement sort by posted date (newest first)
- [ ] Implement sort by institution name (A-Z)
- [ ] Implement sort by location (grouped by region)

**4.5: Pagination Logic** (`static/js/app.js`)
- [ ] Implement page navigation (prev/next)
- [ ] Implement page number buttons
- [ ] Implement jump to page
- [ ] Update URL with page parameter (optional)
- [ ] Scroll to top on page change

**4.6: Card Interactions** (`static/js/app.js`)
- [ ] Implement expand/collapse details
- [ ] Implement modal for full details (optional)
- [ ] Implement save/bookmark (localStorage)
- [ ] Implement share link (copy URL)
- [ ] Open application link in new tab

**4.7: Utility Functions** (`static/js/utils.js`)
- [ ] Date formatting (relative dates: "2 days left")
- [ ] Text truncation
- [ ] URL validation
- [ ] Deadline urgency calculation
- [ ] Search highlighting (optional)

**Acceptance Criteria**:
- All filters work correctly
- Search returns relevant results
- Sorting updates the display
- Pagination works smoothly
- User interactions are responsive (<100ms)
- No JavaScript errors in console

**Performance Considerations**:
- Debounce search and filter inputs
- Use virtual scrolling if needed (for 1000+ listings)
- Lazy load images
- Optimize rendering (avoid re-rendering all cards)

---

## Phase 3E: Site Generation

### Task 5: Build Site Generation Logic
**Status**: ⏸️ Pending  
**Estimated Time**: 1-2 hours

**Subtasks**:

**5.1: Template Renderer** (`scripts/generator/template_renderer.py`)
- [ ] Set up Jinja2 environment
- [ ] Load template from `templates/index.html.jinja`
- [ ] Render template with data
- [ ] Add template filters (date formatting, etc.)

**5.2: Site Builder** (`scripts/generator/build_site.py`)
- [ ] Load `data/processed/jobs.json`
- [ ] Parse and validate JSON
- [ ] Prepare data for template (statistics, listings)
- [ ] Render template with data
- [ ] Write output to `static/index.html`
- [ ] Copy/symlink `jobs.json` to `static/data/`
- [ ] Add command-line interface (CLI)
- [ ] Add logging

**5.3: Build Script Integration**
- [ ] Add build command to `pyproject.toml` (optional)
- [ ] Create shell script for easy building (optional)
- [ ] Document build process in README

**Acceptance Criteria**:
- Build script runs without errors
- Output HTML is valid
- Jobs data is accessible in `static/data/`
- Generated site is ready for deployment

**Usage**:
```bash
poetry run python -m scripts.generator.build_site
```

---

## Phase 3F: Testing & Validation

### Task 6: Test with Current jobs.json
**Status**: ⏸️ Pending  
**Estimated Time**: 2-3 hours

**Subtasks**:

**6.1: Functional Testing**
- [ ] Test with 211 current listings
- [ ] Verify all listings render correctly
- [ ] Test filter combinations (location + job type, etc.)
- [ ] Test search functionality (keywords, phrases)
- [ ] Test sorting (all options)
- [ ] Test pagination (navigate between pages)
- [ ] Test card expand/collapse
- [ ] Test external links (application URLs)
- [ ] Test save/bookmark feature

**6.2: Responsive Testing**
- [ ] Test on desktop (Chrome, Firefox, Safari, Edge)
- [ ] Test on tablet (iPad, Android tablet)
- [ ] Test on mobile (iPhone, Android phone)
- [ ] Test different screen sizes (1920px, 1366px, 768px, 375px)
- [ ] Test orientation changes (portrait/landscape)

**6.3: Performance Testing**
- [ ] Measure page load time (<2 seconds target)
- [ ] Measure time to interactive (<3 seconds target)
- [ ] Test with slow network (3G simulation)
- [ ] Check JavaScript performance (no lag)
- [ ] Check memory usage (no leaks)

**6.4: Accessibility Testing**
- [ ] Test keyboard navigation (tab through filters, cards)
- [ ] Test screen reader compatibility
- [ ] Verify color contrast (WCAG AA)
- [ ] Verify focus indicators
- [ ] Verify ARIA labels
- [ ] Verify semantic HTML

**6.5: Cross-Browser Testing**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers

**6.6: Bug Fixes**
- [ ] Document bugs found during testing
- [ ] Fix critical bugs (P0)
- [ ] Fix high-priority bugs (P1)
- [ ] Defer low-priority bugs (P2) to Phase 4

**Acceptance Criteria**:
- All critical functionality works
- No blocking bugs
- Responsive design works on all tested devices
- Performance meets targets
- Accessibility standards met (WCAG AA)

---

## Phase 3G: Deployment

### Task 7: Deploy MVP to GitHub Pages
**Status**: ⏸️ Pending  
**Estimated Time**: 1-2 hours

**Subtasks**:

**7.1: GitHub Pages Setup**
- [ ] Create/update GitHub repository
- [ ] Configure GitHub Pages (Settings → Pages)
- [ ] Set source to `main` branch, `/static` folder or `/docs` folder
- [ ] Add CNAME (if custom domain)

**7.2: Deployment Process**
- [ ] Copy static site files to deployment folder
- [ ] Commit and push to GitHub
- [ ] Verify deployment (check GitHub Pages URL)
- [ ] Test live site

**7.3: Documentation**
- [ ] Update README.md with deployment instructions
- [ ] Document build and deploy process
- [ ] Add live site URL to README
- [ ] Create deployment checklist

**7.4: Monitoring**
- [ ] Set up analytics (Google Analytics or alternative)
- [ ] Monitor for errors (console logs)
- [ ] Collect user feedback

**Acceptance Criteria**:
- Site is live and accessible
- All features work on live site
- Documentation is up to date
- Analytics are tracking page views

**Deployment URL**: `https://<username>.github.io/<repo-name>/`

---

## Phase 3H: Polish & Enhancement (Optional)

### Task 8: Additional Features (Post-MVP)
**Status**: ⏸️ Pending (Future Work)  
**Estimated Time**: Variable

**Optional Features** (for Phase 4 or later):
- [ ] Dark mode toggle
- [ ] PWA setup (offline access)
- [ ] Auto-refresh when new data available
- [ ] Statistics dashboard with charts
- [ ] Map view of job locations
- [ ] Email notifications for new listings
- [ ] User accounts and saved searches
- [ ] Advanced filtering (salary range, start date)
- [ ] AI-powered job matching
- [ ] Application tracking system

---

## Success Metrics

**Performance**:
- ✅ Page load time < 2 seconds
- ✅ Time to interactive < 3 seconds
- ✅ First contentful paint < 1 second

**Usability**:
- ✅ User can find relevant jobs in < 30 seconds
- ✅ Mobile-friendly (Google PageSpeed > 90)
- ✅ Zero blocking bugs

**Adoption** (Phase 4):
- Track page views
- Monitor search queries
- Collect user feedback

---

## Dependencies

**External**:
- Bootstrap or Tailwind CSS (choose one)
- Jinja2 (already in dependencies)
- GitHub Pages (hosting)

**Internal**:
- `data/processed/jobs.json` (from Phase 2)
- Poetry environment

---

## Testing Strategy

**Unit Tests** (Optional):
- Test template rendering
- Test data loading
- Test filter logic
- Test search logic

**Integration Tests**:
- End-to-end test of build process
- Test with real jobs.json data

**Manual Testing**:
- User acceptance testing
- Visual regression testing
- Cross-browser testing

---

## Risks & Mitigation

1. **Risk**: Large JSON file size (as listings grow)
   - **Mitigation**: Implement pagination, lazy loading, or API endpoint in Phase 4

2. **Risk**: Stale data if pipeline fails
   - **Mitigation**: Display last updated timestamp, implement health check

3. **Risk**: Poor performance on mobile
   - **Mitigation**: Progressive enhancement, mobile-first design

4. **Risk**: Browser compatibility issues
   - **Mitigation**: Use polyfills, test on multiple browsers

5. **Risk**: Deployment issues
   - **Mitigation**: Test locally first, use staging environment

---

## Progress Tracking

**Overall Progress**: 0/7 tasks completed (0%)

| Task | Status | Estimated | Actual |
|------|--------|-----------|--------|
| Task 1: Generator Structure | ⏸️ Pending | 30 min | - |
| Task 2: HTML Template | ⏸️ Pending | 2-3 hrs | - |
| Task 3: CSS Styling | ⏸️ Pending | 2-3 hrs | - |
| Task 4: JavaScript | ⏸️ Pending | 3-4 hrs | - |
| Task 5: Site Generation | ⏸️ Pending | 1-2 hrs | - |
| Task 6: Testing | ⏸️ Pending | 2-3 hrs | - |
| Task 7: Deployment | ⏸️ Pending | 1-2 hrs | - |

**Total Estimated Time**: 12-18 hours

---

## Next Steps

1. ✅ Create proposal (DONE)
2. ✅ Update progress, structure, to-do list (DONE)
3. **Start Task 1**: Create generator script structure
4. Move to Task 2: Design HTML template

---

## Notes

- Using **static site approach** (confirmed by user)
- Target: MVP deployment to GitHub Pages
- Current data: 211 unique job listings
- Expected growth: ~1000 listings over time

---

## References

- **Proposal**: `conversation_cursor/dates/2026-01-03/create-webpage-display-proposal.md`
- **Progress**: `conversation_cursor/progress/latest.md`
- **Structure**: `conversation_cursor/structure/latest.md`
- **Data Schema**: `scripts/processor/schema.py`
- **Sample Data**: `data/processed/jobs.json`
