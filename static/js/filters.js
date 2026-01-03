/**
 * Filtering functionality for job listings
 */

let appState;
let activeFilters = {
    region: '',
    jobTypes: [],
    institutionTypes: [],
    deadline: '',
    status: 'all'
};

/**
 * Initialize filters
 */
function initializeFilters(state) {
    appState = state;
    
    // Set up filter event listeners
    setupFilterListeners();
    
    console.log('Filters initialized');
}

/**
 * Setup filter event listeners
 */
function setupFilterListeners() {
    // Region filter
    const regionSelect = document.getElementById('filter-region');
    if (regionSelect) {
        regionSelect.addEventListener('change', (e) => {
            activeFilters.region = e.target.value;
            applyFilters();
        });
    }
    
    // Job type checkboxes
    const jobTypeCheckboxes = document.querySelectorAll('input[name="job_type"]');
    jobTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            activeFilters.jobTypes = Array.from(jobTypeCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            applyFilters();
        });
    });
    
    // Institution type checkboxes
    const instTypeCheckboxes = document.querySelectorAll('input[name="institution_type"]');
    instTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            activeFilters.institutionTypes = Array.from(instTypeCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            applyFilters();
        });
    });
    
    // Deadline filter
    const deadlineSelect = document.getElementById('filter-deadline');
    if (deadlineSelect) {
        deadlineSelect.addEventListener('change', (e) => {
            activeFilters.deadline = e.target.value;
            applyFilters();
        });
    }
    
    // Sort select
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            sortJobs(e.target.value);
        });
    }
    
    // Clear filters button
    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAllFilters);
    }
}

/**
 * Apply all active filters
 */
function applyFilters() {
    let filtered = [...appState.allJobs];
    
    // Apply region filter
    if (activeFilters.region) {
        filtered = filtered.filter(job => 
            job.location && job.location.toLowerCase().includes(activeFilters.region.toLowerCase())
        );
    }
    
    // Apply job type filter
    if (activeFilters.jobTypes.length > 0) {
        filtered = filtered.filter(job =>
            activeFilters.jobTypes.some(type => 
                job.tags.some(tag => tag.toLowerCase().includes(type.toLowerCase()))
            )
        );
    }
    
    // Apply institution type filter
    if (activeFilters.institutionTypes.length > 0) {
        filtered = filtered.filter(job =>
            activeFilters.institutionTypes.some(type =>
                job.tags.some(tag => tag.toLowerCase().includes(type.toLowerCase()))
            )
        );
    }
    
    // Apply deadline filter
    if (activeFilters.deadline) {
        filtered = filtered.filter(job => matchesDeadlineFilter(job, activeFilters.deadline));
    }
    
    // Update state and render
    appState.setFiltered(filtered);
    
    // Call search filter if search is active
    if (window.currentSearchQuery) {
        window.applySearch();
    } else {
        window.renderJobs();
    }
    
    console.log('Filters applied:', filtered.length, 'jobs match');
}

/**
 * Check if job matches deadline filter
 */
function matchesDeadlineFilter(job, filter) {
    const deadlineText = job.deadline.toLowerCase();
    
    // Active only
    if (filter === 'active') {
        return !deadlineText.includes('expired');
    }
    
    // Within N days
    if (filter === '30' || filter === '60' || filter === '90') {
        const days = parseInt(filter);
        
        // Check if deadline mentions days/weeks/months
        if (deadlineText.includes('day')) {
            const match = deadlineText.match(/(\d+)\s*day/);
            if (match) {
                return parseInt(match[1]) <= days;
            }
        }
        
        if (deadlineText.includes('week')) {
            const match = deadlineText.match(/(\d+)\s*week/);
            if (match) {
                return parseInt(match[1]) * 7 <= days;
            }
        }
        
        if (deadlineText.includes('month')) {
            const match = deadlineText.match(/(\d+)\s*month/);
            if (match) {
                return parseInt(match[1]) * 30 <= days;
            }
        }
        
        // Include "today" and "tomorrow"
        if (deadlineText.includes('today') || deadlineText.includes('tomorrow')) {
            return true;
        }
    }
    
    return true;
}

/**
 * Sort jobs
 */
function sortJobs(sortBy) {
    let sorted = [...appState.filteredJobs];
    
    switch (sortBy) {
        case 'deadline':
            sorted.sort((a, b) => {
                return compareDeadlines(a.deadline, b.deadline);
            });
            break;
            
        case 'posted':
            // Prioritize new listings
            sorted.sort((a, b) => {
                if (a.isNew && !b.isNew) return -1;
                if (!a.isNew && b.isNew) return 1;
                return 0;
            });
            break;
            
        case 'institution':
            sorted.sort((a, b) => {
                return a.institution.localeCompare(b.institution);
            });
            break;
    }
    
    appState.filteredJobs = sorted;
    window.renderJobs();
    
    console.log('Jobs sorted by:', sortBy);
}

/**
 * Compare deadlines for sorting
 */
function compareDeadlines(a, b) {
    const aText = a.toLowerCase();
    const bText = b.toLowerCase();
    
    // Expired go last
    if (aText.includes('expired') && !bText.includes('expired')) return 1;
    if (!aText.includes('expired') && bText.includes('expired')) return -1;
    
    // Today/tomorrow first
    if (aText.includes('today')) return -1;
    if (bText.includes('today')) return 1;
    if (aText.includes('tomorrow')) return -1;
    if (bText.includes('tomorrow')) return 1;
    
    // Extract days for comparison
    const aDays = extractDays(aText);
    const bDays = extractDays(bText);
    
    return aDays - bDays;
}

/**
 * Extract days from deadline text
 */
function extractDays(text) {
    if (text.includes('day')) {
        const match = text.match(/(\d+)\s*day/);
        if (match) return parseInt(match[1]);
    }
    
    if (text.includes('week')) {
        const match = text.match(/(\d+)\s*week/);
        if (match) return parseInt(match[1]) * 7;
    }
    
    if (text.includes('month')) {
        const match = text.match(/(\d+)\s*month/);
        if (match) return parseInt(match[1]) * 30;
    }
    
    return 9999; // Default high value for unknown
}

/**
 * Clear all filters
 */
function clearAllFilters() {
    // Reset filter state
    activeFilters = {
        region: '',
        jobTypes: [],
        institutionTypes: [],
        deadline: '',
        status: 'all'
    };
    
    // Reset UI
    const regionSelect = document.getElementById('filter-region');
    if (regionSelect) regionSelect.value = '';
    
    const deadlineSelect = document.getElementById('filter-deadline');
    if (deadlineSelect) deadlineSelect.value = '';
    
    const checkboxes = document.querySelectorAll('.filter-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    
    // Clear search
    if (window.clearSearch) {
        window.clearSearch();
    }
    
    // Apply filters (will show all)
    applyFilters();
    
    console.log('All filters cleared');
}

// Export functions
window.initializeFilters = initializeFilters;
window.applyFilters = applyFilters;
window.clearAllFilters = clearAllFilters;
