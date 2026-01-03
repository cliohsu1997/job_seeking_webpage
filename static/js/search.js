/**
 * Search functionality for job listings
 */

let appState;
let searchInput;
let searchTimeout;
const SEARCH_DELAY = 300; // ms

let currentSearchQuery = '';

/**
 * Initialize search
 */
function initializeSearch(state) {
    appState = state;
    
    searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        setupSearchListener();
        console.log('Search initialized');
    }
}

/**
 * Setup search event listener
 */
function setupSearchListener() {
    searchInput.addEventListener('input', (e) => {
        // Debounce search
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(() => {
            currentSearchQuery = e.target.value.trim();
            performSearch(currentSearchQuery);
        }, SEARCH_DELAY);
    });
    
    // Clear on escape
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            clearSearch();
        }
    });
}

/**
 * Perform search
 */
function performSearch(query) {
    if (!query) {
        // If search is cleared, apply filters only
        window.applyFilters();
        return;
    }
    
    const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
    
    // Start with filtered jobs (from filters)
    let results = [...appState.filteredJobs];
    
    // Search across multiple fields
    results = results.filter(job => {
        const searchText = [
            job.title,
            job.institution,
            job.department,
            job.location,
            job.description,
            ...job.tags
        ].join(' ').toLowerCase();
        
        // All search terms must match
        return searchTerms.every(term => searchText.includes(term));
    });
    
    // Update state
    appState.filteredJobs = results;
    window.renderJobs();
    
    console.log(`Search "${query}" found ${results.length} jobs`);
}

/**
 * Apply search (called from filters.js)
 */
function applySearch() {
    if (currentSearchQuery) {
        performSearch(currentSearchQuery);
    }
}

/**
 * Clear search
 */
function clearSearch() {
    if (searchInput) {
        searchInput.value = '';
    }
    currentSearchQuery = '';
    
    // Reapply filters without search
    window.applyFilters();
}

/**
 * Highlight search terms (optional enhancement)
 */
function highlightSearchTerms(text, query) {
    if (!query) return text;
    
    const terms = query.split(' ').filter(term => term.length > 0);
    let highlighted = text;
    
    terms.forEach(term => {
        const regex = new RegExp(`(${term})`, 'gi');
        highlighted = highlighted.replace(regex, '<mark>$1</mark>');
    });
    
    return highlighted;
}

// Export functions
window.initializeSearch = initializeSearch;
window.applySearch = applySearch;
window.clearSearch = clearSearch;
window.currentSearchQuery = currentSearchQuery;
