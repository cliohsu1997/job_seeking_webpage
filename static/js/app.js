/**
 * Main application logic for job listings website
 */

// Application state
const AppState = {
    allJobs: [],
    filteredJobs: [],
    currentPage: 1,
    itemsPerPage: 20,
    
    // Initialize state
    init(jobs) {
        this.allJobs = jobs;
        this.filteredJobs = jobs;
    },
    
    // Update filtered jobs
    setFiltered(jobs) {
        this.filteredJobs = jobs;
        this.currentPage = 1; // Reset to first page
    },
    
    // Get jobs for current page
    getCurrentPageJobs() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const result = this.filteredJobs.slice(start, end);
        console.log('getCurrentPageJobs - currentPage:', this.currentPage, 'start:', start, 'end:', end, 'returning:', result.length, 'jobs');
        console.log('First job returned:', result[0]?.title);
        console.log('Full filteredJobs array first 3:', this.filteredJobs.slice(0, 3).map(j => j.title));
        return result;
    },
    
    // Get total pages
    getTotalPages() {
        return Math.ceil(this.filteredJobs.length / this.itemsPerPage);
    }
};

// DOM elements
let jobCardsContainer;
let resultsCount;
let noResults;
let paginationContainer;
let toggleFiltersBtn;
let filtersSidebar;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Get DOM elements
    jobCardsContainer = document.getElementById('job-cards-container');
    resultsCount = document.getElementById('results-count');
    noResults = document.getElementById('no-results');
    paginationContainer = document.getElementById('pagination');
    toggleFiltersBtn = document.getElementById('toggle-filters');
    filtersSidebar = document.getElementById('filters-sidebar');
    
    // Load jobs from data
    loadJobsData();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize filters (from filters.js)
    if (typeof initializeFilters === 'function') {
        initializeFilters(AppState);
    }
    
    // Initialize search (from search.js)
    if (typeof initializeSearch === 'function') {
        initializeSearch(AppState);
    }
    
    console.log('App initialized with', AppState.allJobs.length, 'jobs');
}

/**
 * Load jobs data from JSON
 */
async function loadJobsData() {
    try {
        // Jobs are already embedded in the page (from Jinja2 template)
        // If not, we would fetch from data/jobs.json
        const jobCards = document.querySelectorAll('.job-card');
        const jobs = Array.from(jobCards).map(card => extractJobData(card));
        
        AppState.init(jobs);
        renderJobs();
        
    } catch (error) {
        console.error('Error loading jobs:', error);
        showError('Failed to load job listings. Please refresh the page.');
    }
}

/**
 * Extract job data from card element
 */
function extractJobData(card) {
    const jobId = card.getAttribute('data-job-id');
    const region = card.getAttribute('data-region');
    const institutionType = card.getAttribute('data-institution-type');
    const specializationsAttr = card.getAttribute('data-specializations');
    
    let specializations = [];
    try {
        specializations = specializationsAttr ? JSON.parse(specializationsAttr) : [];
    } catch (e) {
        console.warn('Failed to parse specializations for job', jobId, e);
        specializations = [];
    }
    
    // Extract all data attributes and text content
    const jobData = {
        id: jobId,
        element: card,
        region: region,
        institution_type: institutionType,
        specializations: specializations,
        title: card.querySelector('.job-title')?.textContent.trim() || '',
        institution: card.querySelector('.job-institution span')?.textContent || '',
        department: card.querySelector('.job-department span')?.textContent || '',
        location: card.querySelector('.job-location span')?.textContent || '',
        deadline: card.querySelector('.job-deadline span')?.textContent || '',
        description: card.querySelector('.job-description')?.textContent || '',
        tags: Array.from(card.querySelectorAll('.tag')).map(tag => tag.textContent.trim()),
        isNew: card.querySelector('.badge-new') !== null
    };
    
    console.log('Extracted job:', jobData.title, 'Region:', jobData.region, 'Specializations:', jobData.specializations);
    return jobData;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Toggle filters sidebar (mobile)
    if (toggleFiltersBtn) {
        toggleFiltersBtn.addEventListener('click', toggleFilters);
    }
    
    // Close filters when clicking outside (mobile)
    document.addEventListener('click', (e) => {
        if (filtersSidebar && 
            filtersSidebar.classList.contains('active') &&
            !filtersSidebar.contains(e.target) &&
            !toggleFiltersBtn.contains(e.target)) {
            filtersSidebar.classList.remove('active');
        }
    });
    
    // Job details toggle
    document.addEventListener('click', (e) => {
        if (e.target.matches('.btn-details') || e.target.closest('.btn-details')) {
            const btn = e.target.matches('.btn-details') ? e.target : e.target.closest('.btn-details');
            toggleJobDetails(btn);
        }
    });
}

/**
 * Toggle filters sidebar (mobile)
 */
function toggleFilters() {
    if (filtersSidebar) {
        filtersSidebar.classList.toggle('active');
    }
}

/**
 * Toggle job details
 */
function toggleJobDetails(btn) {
    const jobId = btn.getAttribute('data-job-id');
    const detailsEl = document.getElementById(`details-${jobId}`);
    
    if (detailsEl) {
        const isVisible = detailsEl.style.display !== 'none';
        detailsEl.style.display = isVisible ? 'none' : 'block';
        btn.textContent = isVisible ? 'View Details' : 'Hide Details';
    }
}

/**
 * Render jobs to the page
 */
function renderJobs() {
    console.log('=== renderJobs CALLED ===');
    const jobs = AppState.getCurrentPageJobs();
    
    // Update results count
    updateResultsCount();
    
    // Get the container
    const container = document.getElementById('job-cards-container');
    if (!container) return;
    
    console.log('Rendering page with', jobs.length, 'jobs');
    console.log('Reordering DOM - first 3 jobs in filteredJobs:', AppState.filteredJobs.slice(0, 3).map(j => j.title));
    
    // FIRST: Hide ALL jobs (including non-filtered ones)
    AppState.allJobs.forEach(job => {
        if (job.element) {
            job.element.style.display = 'none';
        }
    });
    
    // SECOND: Re-append ALL filtered jobs in sorted order
    // This ensures the DOM order matches the sorted order
    AppState.filteredJobs.forEach((job, idx) => {
        if (job.element) {
            container.appendChild(job.element);
            if (idx < 3) {
                console.log(`Reordered position ${idx}: ${job.title}, institution: ${job.institution}`);
            }
        }
    });
    
    // THIRD: Show only the current page jobs
    if (jobs.length === 0) {
        showNoResults();
    } else {
        hideNoResults();
        jobs.forEach((job, index) => {
            if (job.element) {
                job.element.style.display = 'block';
                console.log(`Job ${index}:`, job.title);
            }
        });
    }
    
    // Render pagination
    renderPagination();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Update results count
 */
function updateResultsCount() {
    if (resultsCount) {
        resultsCount.textContent = AppState.filteredJobs.length;
    }
}

/**
 * Show no results message
 */
function showNoResults() {
    if (noResults) {
        noResults.style.display = 'block';
    }
}

/**
 * Hide no results message
 */
function hideNoResults() {
    if (noResults) {
        noResults.style.display = 'none';
    }
}

/**
 * Render pagination
 */
function renderPagination() {
    if (!paginationContainer) return;
    
    const totalPages = AppState.getTotalPages();
    
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `
        <button class="pagination-btn" 
                onclick="changePage(${AppState.currentPage - 1})"
                ${AppState.currentPage === 1 ? 'disabled' : ''}>
            ← Previous
        </button>
    `;
    
    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, AppState.currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    // Adjust start if we're near the end
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    // First page + ellipsis
    if (startPage > 1) {
        html += `<button class="pagination-btn" onclick="changePage(1)">1</button>`;
        if (startPage > 2) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <button class="pagination-btn ${i === AppState.currentPage ? 'active' : ''}" 
                    onclick="changePage(${i})">
                ${i}
            </button>
        `;
    }
    
    // Ellipsis + last page
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
        html += `<button class="pagination-btn" onclick="changePage(${totalPages})">${totalPages}</button>`;
    }
    
    // Next button
    html += `
        <button class="pagination-btn" 
                onclick="changePage(${AppState.currentPage + 1})"
                ${AppState.currentPage === totalPages ? 'disabled' : ''}>
            Next →
        </button>
    `;
    
    paginationContainer.innerHTML = html;
}

/**
 * Change page
 */
function changePage(page) {
    const totalPages = AppState.getTotalPages();
    if (page < 1 || page > totalPages) return;
    
    AppState.currentPage = page;
    renderJobs();
}

/**
 * Show error message
 */
function showError(message) {
    if (jobCardsContainer) {
        jobCardsContainer.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Export functions for other modules
window.AppState = AppState;
window.renderJobs = renderJobs;
window.changePage = changePage;
