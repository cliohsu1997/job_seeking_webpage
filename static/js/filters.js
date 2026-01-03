/**
 * Filtering functionality for job listings
 */

let activeFilters = {
    region: '',
    jobTypes: [],
    institutionTypes: [],
    specializations: [],
    deadline: '',
    status: 'all'
};
let currentSort = 'deadline'; // Track current sort preference

/**
 * Initialize filters
 */
function initializeFilters(state) {
    // Use global AppState from window
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
            console.log('Region filter changed:', activeFilters.region);
            applyFilters();
        });
    }
    
    // Job type checkboxes
    const jobTypeCheckboxes = document.querySelectorAll('input[name="job_type"]');
    console.log('Found job type checkboxes:', jobTypeCheckboxes.length);
    jobTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            activeFilters.jobTypes = Array.from(jobTypeCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            console.log('Job type filter changed:', activeFilters.jobTypes);
            applyFilters();
        });
    });
    
    // Institution type checkboxes
    const instTypeCheckboxes = document.querySelectorAll('input[name="institution_type"]');
    console.log('Found institution type checkboxes:', instTypeCheckboxes.length);
    instTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            activeFilters.institutionTypes = Array.from(instTypeCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            console.log('Institution type filter changed:', activeFilters.institutionTypes);
            applyFilters();
        });
    });
    
    // Specialization checkboxes
    const specializationCheckboxes = document.querySelectorAll('input[name="specialization"]');
    console.log('Found specialization checkboxes:', specializationCheckboxes.length);
    specializationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            activeFilters.specializations = Array.from(specializationCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            console.log('Specialization filter changed:', activeFilters.specializations);
            applyFilters();
        });
    });
    
    // Deadline filter
    const deadlineSelect = document.getElementById('filter-deadline');
    if (deadlineSelect) {
        deadlineSelect.addEventListener('change', (e) => {
            activeFilters.deadline = e.target.value;
            console.log('Deadline filter changed:', activeFilters.deadline);
            applyFilters();
        });
    }
    
    // Sort select
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            currentSort = e.target.value;
            console.log('Sort changed:', currentSort);
            sortJobs(currentSort);
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
    console.log('Applying filters:', activeFilters);
    let filtered = [...window.AppState.allJobs];
    console.log('Starting with', filtered.length, 'jobs');
    
    // Apply region filter
    if (activeFilters.region) {
        console.log('Filtering by region:', activeFilters.region);
        // Show first few regions for debugging
        filtered.slice(0, 3).forEach(job => {
            console.log('Sample region:', job.region);
        });
        
        filtered = filtered.filter(job => 
            job.region && job.region.toLowerCase() === activeFilters.region.toLowerCase()
        );
        console.log('After region filter:', filtered.length, 'jobs');
    }
    
    // Apply job type filter
    if (activeFilters.jobTypes.length > 0) {
        filtered = filtered.filter(job => {
            const match = activeFilters.jobTypes.some(type => 
                job.tags.some(tag => tag.toLowerCase().includes(type.toLowerCase()))
            );
            return match;
        });
        console.log('After job type filter:', filtered.length, 'jobs');
    }
    
    // Apply institution type filter
    if (activeFilters.institutionTypes.length > 0) {
        filtered = filtered.filter(job => {
            const match = activeFilters.institutionTypes.includes(job.institution_type);
            return match;
        });
        console.log('After institution type filter:', filtered.length, 'jobs');
    }
    
    // Apply specialization filter
    if (activeFilters.specializations.length > 0) {
        filtered = filtered.filter(job => {
            // Job must have at least one of the selected specializations
            if (!job.specializations || job.specializations.length === 0) {
                return false;
            }
            const match = activeFilters.specializations.some(selectedSpec => 
                job.specializations.includes(selectedSpec)
            );
            return match;
        });
        console.log('After specialization filter:', filtered.length, 'jobs');
    }
    
    // Apply deadline filter
    if (activeFilters.deadline) {
        console.log('Filtering by deadline:', activeFilters.deadline);
        const before = filtered.length;
        filtered = filtered.filter(job => matchesDeadlineFilter(job, activeFilters.deadline));
        console.log('After deadline filter:', filtered.length, 'jobs (was', before, ')');
    }
    
    // Update state and render
    window.AppState.setFiltered(filtered);
    
    // Reapply current sort to the filtered results
    if (currentSort && currentSort !== 'deadline') {
        console.log('Reapplying sort:', currentSort);
        sortJobs(currentSort);
    } else {
        // Call search filter if search is active
        if (window.currentSearchQuery) {
            window.applySearch();
        } else {
            window.renderJobs();
        }
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
    console.log('Sorting by:', sortBy, 'Current filtered jobs:', window.AppState.filteredJobs.length);
    let sorted = [...window.AppState.filteredJobs];
    
    switch (sortBy) {
        case 'deadline':
            console.log('Sorting by deadline');
            sorted.sort((a, b) => {
                const result = compareDeadlines(a.deadline, b.deadline);
                return result;
            });
            break;
            
        case 'posted':
            console.log('Sorting by posted date (new first)');
            sorted.sort((a, b) => {
                if (a.isNew && !b.isNew) return -1;
                if (!a.isNew && b.isNew) return 1;
                return 0;
            });
            break;
            
        case 'institution':
            console.log('Sorting by institution name');
            // Debug: log first few institutions before sort
            console.log('Before sort - first 5 institutions:', sorted.slice(0, 5).map(j => j.institution || '(empty)'));
            sorted.sort((a, b) => {
                const instA = (a.institution || '').toLowerCase();
                const instB = (b.institution || '').toLowerCase();
                return instA.localeCompare(instB);
            });
            // Debug: log first few institutions after sort
            console.log('After sort - first 5 institutions:', sorted.slice(0, 5).map(j => j.institution || '(empty)'));
            break;
    }
    
    window.AppState.filteredJobs = sorted;
    window.AppState.currentPage = 1; // Reset to first page
    window.renderJobs();
    
    console.log('Jobs sorted by:', sortBy, 'First 3 titles:', sorted.slice(0, 3).map(j => j.title));
}

/**
 * Compare deadlines for sorting
 */
function compareDeadlines(a, b) {
    const aText = a.toLowerCase();
    const bText = b.toLowerCase();
    
    console.log('Comparing deadlines:', aText, 'vs', bText);
    
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
    
    console.log('Extracted days:', aDays, 'vs', bDays, 'result:', aDays - bDays);
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
        specializations: [],
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
window.sortJobs = sortJobs;

// Expose currentSort for search.js to use
Object.defineProperty(window, 'currentSort', {
    get: function() { return currentSort; },
    set: function(value) { currentSort = value; }
});
