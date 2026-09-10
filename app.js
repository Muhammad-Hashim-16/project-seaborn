/**
 * SeabornGallery — Main Application
 * ==================================
 * Handles data loading, rendering, filtering, sorting, modal, theme toggling,
 * keyboard shortcuts, PWA install, and all interactive behavior.
 *
 * Dependencies: search.js (loaded before this file), Lucide icons, Highlight.js
 */

/* ========================================================================
   CONFIGURATION
   ======================================================================== */

/** @type {Object} Application configuration constants */
const CONFIG = {
  dataFile: './data.json',
  figuresDir: './figures/',
  codeSnippetsDir: './code_snippets/',
  storageKey: 'seaborngallery-theme',
  animationStagger: 40,
  scrollTopThreshold: 400,
  toastDuration: 2200,
  searchDebounce: 220,
  maxTagsOnCard: 3,
};

/* ========================================================================
   STATE
   ======================================================================== */

/** @type {Object} Application state */
const state = {
  plots: [],
  filteredPlots: [],
  currentModalIndex: -1,
  activeFilters: { difficulty: 'all', tags: [], search: '' },
  theme: 'dark',
  sortOrder: 'default',
  renderedPlotIds: new Set(),
};

/* ========================================================================
   UTILITY FUNCTIONS
   ======================================================================== */

/**
 * Creates a debounced version of a function.
 * @param {Function} fn - The function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

/**
 * Creates a throttled version of a function.
 * @param {Function} fn - The function to throttle
 * @param {number} limit - Minimum time between calls in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(fn, limit) {
  let inThrottle = false;
  return function (...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => { inThrottle = false; }, limit);
    }
  };
}

/**
 * Get numeric order for difficulty level.
 * @param {string} difficulty - "Beginner", "Intermediate", or "Advanced"
 * @returns {number} 0, 1, or 2
 */
function getDifficultyOrder(difficulty) {
  const map = { 'Beginner': 0, 'Intermediate': 1, 'Advanced': 2 };
  return map[difficulty] ?? 0;
}

/**
 * Escape HTML special characters to prevent XSS.
 * @param {string} str - Raw string
 * @returns {string} Escaped string
 */
function sanitizeHTML(str) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' };
  return String(str).replace(/[&<>"']/g, (c) => map[c]);
}

/* ========================================================================
   INITIALIZATION
   ======================================================================== */

/**
 * Initialize the application.
 * Sets up theme, loads data, binds all event listeners.
 */
function init() {
  // Read theme from localStorage (anti-flicker script already set the attribute)
  state.theme = localStorage.getItem(CONFIG.storageKey) || 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeIcon();

  // Load data
  loadData();

  // Event listeners
  setupSearchListeners();
  setupFilterListeners();
  setupModalListeners();
  setupScrollListeners();
  setupKeyboardListeners();
  setupPWAListeners();

  // Initialize Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

/* ========================================================================
   DATA LOADING
   ======================================================================== */

/**
 * Load plot data from data.json.
 * Shows skeleton loading state, then renders the gallery.
 */
async function loadData() {
  const grid = document.getElementById('plots-grid');
  const noResults = document.getElementById('no-results');

  // Show skeleton loading cards
  showSkeletonCards(grid, 9);

  try {
    const response = await fetch(CONFIG.dataFile);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Validate data is an array (FIX 14)
    if (!Array.isArray(data)) {
      throw new Error('data.json is not a valid array');
    }

    if (data.length === 0) {
      removeSkeletonCards(grid);
      showErrorState(grid, 'data.json is empty. Run splitter.py first, then refresh.');
      return;
    }

    // Validate entries have required fields
    data.forEach((entry, i) => {
      if (!entry.id || !entry.name || !entry.difficulty || !entry.image) {
        console.warn(`[SeabornGallery] Plot entry ${i} missing required fields:`, entry);
      }
    });

    state.plots = data;
    state.filteredPlots = [...data];

    removeSkeletonCards(grid);
    renderStats();
    renderFilterPills();
    renderGrid();

    // Handle ?search=focus from about.html (FIX 11)
    const params = new URLSearchParams(window.location.search);
    if (params.get('search') === 'focus') {
      const searchInput = document.getElementById('search-input');
      if (searchInput) {
        setTimeout(() => searchInput.focus(), 300);
      }
    }

  } catch (err) {
    console.error('[SeabornGallery] Failed to load data:', err);
    removeSkeletonCards(grid);
    showErrorState(grid, 'Failed to load plots. Run splitter.py first, then refresh.');
  }
}

/**
 * Show skeleton loading cards.
 * @param {HTMLElement} grid - The grid container
 * @param {number} count - Number of skeleton cards
 */
function showSkeletonCards(grid, count) {
  for (let i = 0; i < count; i++) {
    const card = document.createElement('div');
    card.className = 'skeleton-card';
    card.innerHTML = `
      <div class="skeleton-img"></div>
      <div class="skeleton-body">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line medium"></div>
      </div>
    `;
    grid.appendChild(card);
  }
}

/**
 * Remove all skeleton cards from the grid.
 * @param {HTMLElement} grid - The grid container
 */
function removeSkeletonCards(grid) {
  grid.querySelectorAll('.skeleton-card').forEach((el) => el.remove());
}

/**
 * Show an error state in the grid.
 * @param {HTMLElement} grid - The grid container
 * @param {string} message - Error message to display
 */
function showErrorState(grid, message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-state';
  errorDiv.innerHTML = `
    <i data-lucide="alert-triangle" width="48" height="48" class="error-state-icon"></i>
    <h3 class="error-state-title">Could not load plot data</h3>
    <p class="error-state-text">${sanitizeHTML(message)}</p>
  `;
  grid.appendChild(errorDiv);
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

/* ========================================================================
   RENDERING
   ======================================================================== */

/**
 * Update the hero stats with actual data counts.
 */
function renderStats() {
  const statPlots = document.getElementById('stat-plots');
  const statTags = document.getElementById('stat-tags');

  if (statPlots) {
    statPlots.textContent = state.plots.length;
  }

  if (statTags) {
    const allTags = new Set();
    state.plots.forEach((p) => {
      if (p.tags) p.tags.forEach((t) => allTags.add(t));
    });
    statTags.textContent = allTags.size > 0 ? allTags.size : '40+';
  }
}

/**
 * Generate and render tag filter pills from data.
 */
function renderFilterPills() {
  const filterRow = document.getElementById('filter-row');
  if (!filterRow) return;

  // Collect unique tags, sorted alphabetically
  const tagSet = new Set();
  state.plots.forEach((p) => {
    if (p.tags) p.tags.forEach((t) => tagSet.add(t));
  });
  const sortedTags = [...tagSet].sort();

  // Add tag pills after the divider
  sortedTags.forEach((tag) => {
    const pill = document.createElement('button');
    pill.className = 'filter-pill';
    pill.dataset.filter = tag;
    pill.dataset.type = 'tag';
    pill.textContent = tag;
    filterRow.appendChild(pill);
  });

  // Add click listeners to ALL pills (including pre-existing ones)
  filterRow.querySelectorAll('.filter-pill').forEach((pill) => {
    pill.addEventListener('click', handleFilterClick);
  });
}

/**
 * Render the plots grid with current filtered data.
 */
function renderGrid() {
  const grid = document.getElementById('plots-grid');
  const noResults = document.getElementById('no-results');
  const resultsText = document.getElementById('results-text');
  if (!grid) return;

  // Remove existing cards (but preserve #no-results)
  grid.querySelectorAll('.plot-card').forEach((el) => el.remove());
  grid.querySelectorAll('.error-state').forEach((el) => el.remove());

  if (state.filteredPlots.length === 0) {
    if (noResults) noResults.style.display = 'flex';
    if (resultsText) resultsText.textContent = `Showing 0 of ${state.plots.length} plots`;
    return;
  }

  if (noResults) noResults.style.display = 'none';

  // Render cards
  state.filteredPlots.forEach((plot, index) => {
    const card = createCardElement(plot, index);
    grid.appendChild(card);
  });

  // Update results text
  if (resultsText) {
    resultsText.textContent = `Showing ${state.filteredPlots.length} of ${state.plots.length} plots`;
  }

  // Re-initialize Lucide icons in newly created cards
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

/**
 * Create a single plot card DOM element.
 * @param {Object} plot - Plot data object
 * @param {number} index - Index in the filtered array (for stagger animation)
 * @returns {HTMLElement} The card article element
 */
function createCardElement(plot, index) {
  const article = document.createElement('article');
  article.className = 'plot-card';
  article.dataset.id = plot.id;
  article.dataset.difficulty = plot.difficulty;
  article.dataset.tags = (plot.tags || []).join(',');
  article.dataset.name = plot.name;
  article.setAttribute('role', 'button');
  article.setAttribute('tabindex', '0');
  article.setAttribute('aria-label', `Open plot ${plot.id}: ${plot.name}`);

  // Determine badge class
  const badgeClass = `badge-${plot.difficulty.toLowerCase()}`;

  // Build tags HTML (max CONFIG.maxTagsOnCard)
  const tags = plot.tags || [];
  let tagsHTML = '';
  const visibleTags = tags.slice(0, CONFIG.maxTagsOnCard);
  visibleTags.forEach((tag) => {
    tagsHTML += `<span class="tag-pill">${sanitizeHTML(tag)}</span>`;
  });
  if (tags.length > CONFIG.maxTagsOnCard) {
    tagsHTML += `<span class="tag-pill">+${tags.length - CONFIG.maxTagsOnCard} more</span>`;
  }

  article.innerHTML = `
    <div class="card-image-wrapper">
      <img src="${sanitizeHTML(plot.image)}" alt="${sanitizeHTML(plot.name)}" loading="lazy" />
      <div class="card-overlay">
        <span class="expand-hint">
          <i data-lucide="eye" width="16" height="16"></i> View Plot
        </span>
      </div>
      <span class="difficulty-badge ${badgeClass}">${sanitizeHTML(plot.difficulty)}</span>
    </div>
    <div class="card-body">
      <div class="card-meta">
        <span class="plot-number">#${plot.id}</span>
        <span class="plot-library-badge">seaborn</span>
      </div>
      <h3 class="plot-name">${sanitizeHTML(plot.name)}</h3>
      <div class="card-tags">${tagsHTML}</div>
    </div>
  `;

  // Image error handler: show placeholder
  const img = article.querySelector('img');
  img.addEventListener('error', () => {
    const wrapper = article.querySelector('.card-image-wrapper');
    img.remove();
    const placeholder = document.createElement('div');
    placeholder.className = 'image-placeholder';
    placeholder.textContent = `#${plot.id}`;
    wrapper.insertBefore(placeholder, wrapper.firstChild);
  });

  // Click and keyboard handlers
  article.addEventListener('click', () => openModal(plot.id));
  article.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openModal(plot.id);
    }
  });

  // Animation (FIX 8: only animate if not yet rendered)
  if (!state.renderedPlotIds.has(plot.id)) {
    article.classList.add('animate-in');
    article.style.animationDelay = `${index * CONFIG.animationStagger}ms`;
    state.renderedPlotIds.add(plot.id);
  }

  return article;
}

/* ========================================================================
   FILTERING & SORTING
   ======================================================================== */

/**
 * Handle filter pill clicks.
 * @param {Event} e - Click event
 */
function handleFilterClick(e) {
  const pill = e.currentTarget;
  const filter = pill.dataset.filter;
  const type = pill.dataset.type;

  if (type === 'category' && filter === 'all') {
    // Reset all filters
    resetAllFilters();
    return;
  }

  if (type === 'difficulty') {
    // Toggle difficulty: if same clicked, reset to all
    if (state.activeFilters.difficulty === filter) {
      state.activeFilters.difficulty = 'all';
    } else {
      state.activeFilters.difficulty = filter;
    }
    // Deactivate "All" pill
    updatePillStates();
    applyFilters();
    return;
  }

  if (type === 'tag') {
    // Toggle tag (multi-select)
    const idx = state.activeFilters.tags.indexOf(filter);
    if (idx > -1) {
      state.activeFilters.tags.splice(idx, 1);
    } else {
      state.activeFilters.tags.push(filter);
    }
    updatePillStates();
    applyFilters();
    return;
  }
}

/**
 * Reset all filters to default state.
 */
function resetAllFilters() {
  state.activeFilters.difficulty = 'all';
  state.activeFilters.tags = [];
  state.activeFilters.search = '';
  state.sortOrder = 'default';

  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.value = '';
    searchInput.closest('.search-wrapper')?.classList.remove('has-value');
  }

  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) sortSelect.value = 'default';

  updatePillStates();
  applyFilters();
}

/**
 * Update visual active states on all filter pills.
 */
function updatePillStates() {
  const filterRow = document.getElementById('filter-row');
  if (!filterRow) return;

  filterRow.querySelectorAll('.filter-pill').forEach((pill) => {
    const filter = pill.dataset.filter;
    const type = pill.dataset.type;

    if (type === 'category' && filter === 'all') {
      // "All" active if no difficulty and no tags
      pill.classList.toggle('active',
        state.activeFilters.difficulty === 'all' && state.activeFilters.tags.length === 0
      );
    } else if (type === 'difficulty') {
      pill.classList.toggle('active', state.activeFilters.difficulty === filter);
    } else if (type === 'tag') {
      pill.classList.toggle('active', state.activeFilters.tags.includes(filter));
    }
  });
}

/**
 * Apply all active filters and sort, then re-render the grid.
 */
function applyFilters() {
  let result = [...state.plots];

  // Difficulty filter
  if (state.activeFilters.difficulty !== 'all') {
    result = result.filter((p) => p.difficulty === state.activeFilters.difficulty);
  }

  // Tag filter (OR logic: show plot if it has ANY of the selected tags)
  if (state.activeFilters.tags.length > 0) {
    result = result.filter((p) => {
      if (!p.tags) return false;
      return state.activeFilters.tags.some((tag) => p.tags.includes(tag));
    });
  }

  // Search filter
  if (state.activeFilters.search.trim()) {
    result = window.MatplotSearch.filter(result, state.activeFilters.search);
  }

  // Sort
  if (state.sortOrder === 'beginner-first') {
    result.sort((a, b) => getDifficultyOrder(a.difficulty) - getDifficultyOrder(b.difficulty) || a.id - b.id);
  } else if (state.sortOrder === 'advanced-first') {
    result.sort((a, b) => getDifficultyOrder(b.difficulty) - getDifficultyOrder(a.difficulty) || a.id - b.id);
  } else {
    result.sort((a, b) => a.id - b.id);
  }

  state.filteredPlots = result;
  renderGrid();
}

/* ========================================================================
   SEARCH
   ======================================================================== */

/**
 * Set up search input event listeners.
 */
function setupSearchListeners() {
  const searchInput = document.getElementById('search-input');
  const searchClear = document.getElementById('search-clear');
  const searchBtn = document.getElementById('search-btn');

  if (searchInput) {
    const debouncedSearch = debounce((value) => {
      state.activeFilters.search = value;
      applyFilters();
    }, CONFIG.searchDebounce);

    searchInput.addEventListener('input', (e) => {
      const value = e.target.value;
      const wrapper = searchInput.closest('.search-wrapper');

      if (value.length > 0) {
        wrapper?.classList.add('has-value');
      } else {
        wrapper?.classList.remove('has-value');
      }

      debouncedSearch(value);
    });
  }

  if (searchClear) {
    searchClear.addEventListener('click', () => {
      if (searchInput) {
        searchInput.value = '';
        searchInput.closest('.search-wrapper')?.classList.remove('has-value');
        searchInput.focus();
        state.activeFilters.search = '';
        applyFilters();
      }
    });
  }

  // Search button (navbar): focus search or open overlay on mobile
  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      const isMobile = window.innerWidth <= 640;
      if (isMobile) {
        openSearchOverlay();
      } else {
        if (searchInput) searchInput.focus();
      }
    });
  }

  // Mobile search overlay
  const overlayClose = document.getElementById('search-overlay-close');
  const overlayInput = document.getElementById('search-overlay-input');
  const overlayClear = document.getElementById('search-overlay-clear');

  if (overlayClose) {
    overlayClose.addEventListener('click', closeSearchOverlay);
  }

  if (overlayInput) {
    const debouncedOverlaySearch = debounce((value) => {
      state.activeFilters.search = value;
      if (searchInput) searchInput.value = value;
      applyFilters();
    }, CONFIG.searchDebounce);

    overlayInput.addEventListener('input', (e) => {
      debouncedOverlaySearch(e.target.value);
    });
  }

  if (overlayClear) {
    overlayClear.addEventListener('click', () => {
      if (overlayInput) overlayInput.value = '';
      if (searchInput) searchInput.value = '';
      searchInput?.closest('.search-wrapper')?.classList.remove('has-value');
      state.activeFilters.search = '';
      applyFilters();
    });
  }
}

/**
 * Open the mobile search overlay.
 */
function openSearchOverlay() {
  const overlay = document.getElementById('search-overlay');
  if (overlay) {
    overlay.classList.add('active');
    const input = document.getElementById('search-overlay-input');
    if (input) setTimeout(() => input.focus(), 100);
  }
}

/**
 * Close the mobile search overlay.
 */
function closeSearchOverlay() {
  const overlay = document.getElementById('search-overlay');
  if (overlay) overlay.classList.remove('active');
}

/* ========================================================================
   FILTER EVENT SETUP
   ======================================================================== */

/**
 * Set up filter-related event listeners.
 */
function setupFilterListeners() {
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sortOrder = e.target.value;
      applyFilters();
    });
  }

  // No results reset button (FIX 12)
  const resetBtn = document.getElementById('reset-filters-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', resetAllFilters);
  }
}

/* ========================================================================
   MODAL
   ======================================================================== */

/**
 * Set up modal event listeners.
 */
function setupModalListeners() {
  const closeBtn = document.getElementById('modal-close-btn');
  const prevBtn = document.getElementById('prev-plot-btn');
  const nextBtn = document.getElementById('next-plot-btn');
  const copyBtn = document.getElementById('copy-code-btn');
  const overlay = document.getElementById('modal-overlay');

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (prevBtn) prevBtn.addEventListener('click', () => navigateModal('prev'));
  if (nextBtn) nextBtn.addEventListener('click', () => navigateModal('next'));

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const codeEl = document.getElementById('modal-code');
      if (codeEl) copyCode(codeEl.textContent);
    });
  }

  // Close on overlay background click (FIX 9)
  if (overlay) {
    overlay.addEventListener('click', (e) => {
      if (e.target.id === 'modal-overlay') closeModal();
    });
  }
}

/**
 * Open the modal for a specific plot.
 * @param {number} plotId - The plot ID to display
 */
async function openModal(plotId) {
  const plot = state.filteredPlots.find((p) => p.id === plotId);
  if (!plot) return;

  state.currentModalIndex = state.filteredPlots.indexOf(plot);

  // Load code if not cached
  if (!plot.code) {
    try {
      const resp = await fetch(`${CONFIG.codeSnippetsDir}${plot.id}.txt`);
      if (resp.ok) {
        plot.code = await resp.text();
      } else {
        plot.code = '# Code file not found.\n# Run splitter.py to generate code snippets.';
      }
    } catch (err) {
      plot.code = '# Code file not found.\n# Run splitter.py to generate code snippets.';
    }
  }

  // Populate modal elements
  const plotNumber = document.getElementById('modal-plot-number');
  const plotName = document.getElementById('modal-plot-name');
  const diffBadge = document.getElementById('modal-difficulty-badge');
  const modalImage = document.getElementById('modal-image');
  const modalCode = document.getElementById('modal-code');
  const modalTags = document.getElementById('modal-tags');
  const modalCounter = document.getElementById('modal-counter');
  const prevBtn = document.getElementById('prev-plot-btn');
  const nextBtn = document.getElementById('next-plot-btn');

  if (plotNumber) plotNumber.textContent = `#${plot.id}`;
  if (plotName) {
    plotName.textContent = plot.name;
    plotName.title = plot.name;
  }

  if (diffBadge) {
    diffBadge.textContent = plot.difficulty;
    diffBadge.className = `difficulty-badge badge-${plot.difficulty.toLowerCase()}`;
  }

  // Image with transition (FIX 3)
  if (modalImage) {
    modalImage.style.opacity = '0';
    modalImage.src = plot.image;
    modalImage.alt = plot.name;
    modalImage.onload = () => { modalImage.style.opacity = '1'; };
    modalImage.onerror = () => { modalImage.style.opacity = '1'; };
  }

  // Code with highlight.js (FIX 2)
  if (modalCode) {
    modalCode.textContent = plot.code;
    setTimeout(() => {
      delete modalCode.dataset.highlighted;
      if (typeof hljs !== 'undefined') {
        hljs.highlightElement(modalCode);
      }
    }, 0);
  }

  // Tags
  if (modalTags) {
    modalTags.innerHTML = '';
    (plot.tags || []).forEach((tag) => {
      const pill = document.createElement('span');
      pill.className = 'tag-pill';
      pill.textContent = tag;
      modalTags.appendChild(pill);
    });
  }

  // Counter
  if (modalCounter) {
    modalCounter.textContent = `${state.currentModalIndex + 1} / ${state.filteredPlots.length}`;
  }

  // Navigation buttons
  if (prevBtn) prevBtn.disabled = state.currentModalIndex <= 0;
  if (nextBtn) nextBtn.disabled = state.currentModalIndex >= state.filteredPlots.length - 1;

  // Reset copy button
  const copyBtn = document.getElementById('copy-code-btn');
  const copyText = document.getElementById('copy-btn-text');
  if (copyBtn) copyBtn.classList.remove('copied');
  if (copyText) copyText.textContent = 'Copy';

  // Show modal
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  // Re-initialize Lucide icons (FIX 6)
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // Focus management for accessibility
  const closeBtn = document.getElementById('modal-close-btn');
  if (closeBtn) setTimeout(() => closeBtn.focus(), 100);
}

/**
 * Close the modal.
 */
function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
  state.currentModalIndex = -1;

  // Clear image after transition (prevent stale image flash)
  setTimeout(() => {
    const img = document.getElementById('modal-image');
    if (img) img.src = '';
  }, 300);
}

/**
 * Navigate to prev or next plot in the modal.
 * @param {'prev'|'next'} direction - Navigation direction
 */
function navigateModal(direction) {
  let newIndex;
  if (direction === 'prev') {
    newIndex = state.currentModalIndex - 1;
  } else {
    newIndex = state.currentModalIndex + 1;
  }

  if (newIndex >= 0 && newIndex < state.filteredPlots.length) {
    openModal(state.filteredPlots[newIndex].id);
  }
}

/* ========================================================================
   COPY TO CLIPBOARD
   ======================================================================== */

/**
 * Copy text to clipboard with fallback for non-HTTPS environments (FIX 7).
 * @param {string} text - Text to copy
 */
async function copyCode(text) {
  let success = false;

  try {
    await navigator.clipboard.writeText(text);
    success = true;
  } catch (err) {
    // Fallback: textarea method
    try {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      textarea.style.top = '-9999px';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      success = true;
    } catch (fallbackErr) {
      console.error('[SeabornGallery] Copy failed:', fallbackErr);
    }
  }

  if (success) {
    const btn = document.getElementById('copy-code-btn');
    const btnText = document.getElementById('copy-btn-text');

    if (btn) btn.classList.add('copied');
    if (btnText) btnText.textContent = 'Copied!';

    showToast('Copied to clipboard', 'success');

    setTimeout(() => {
      if (btn) btn.classList.remove('copied');
      if (btnText) btnText.textContent = 'Copy';
    }, 2000);
  }
}

/* ========================================================================
   TOAST
   ======================================================================== */

/** @type {number|null} Toast timeout ID */
let toastTimeout = null;

/**
 * Show a toast notification.
 * @param {string} message - Message to display
 * @param {string} type - Toast type (e.g., 'success')
 */
function showToast(message, type) {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toast-message');
  if (!toast || !msgEl) return;

  msgEl.textContent = message;

  // Clear existing timeout
  if (toastTimeout) clearTimeout(toastTimeout);

  toast.classList.add('show');
  toastTimeout = setTimeout(() => {
    toast.classList.remove('show');
  }, CONFIG.toastDuration);
}

/* ========================================================================
   THEME TOGGLE
   ======================================================================== */

/**
 * Toggle between dark and light themes.
 */
function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  localStorage.setItem(CONFIG.storageKey, state.theme);
  updateThemeIcon();
}

/**
 * Update the theme toggle button icon.
 */
function updateThemeIcon() {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;

  // Replace the icon
  const iconName = state.theme === 'dark' ? 'moon' : 'sun';
  btn.innerHTML = `<i data-lucide="${iconName}" width="18" height="18"></i>`;

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

/* ========================================================================
   SCROLL HANDLING
   ======================================================================== */

/**
 * Set up scroll-related event listeners.
 */
function setupScrollListeners() {
  const scrollTopBtn = document.getElementById('scroll-top-btn');
  const themeToggle = document.getElementById('theme-toggle');

  // Theme toggle
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  // Scroll to top button
  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Throttled scroll handler
  window.addEventListener('scroll', throttle(handleScroll, 100), { passive: true });
}

/**
 * Handle scroll events: progress bar, scroll-to-top button, navbar shadow.
 */
function handleScroll() {
  const scrollY = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const scrollPercent = docHeight > 0 ? (scrollY / docHeight) * 100 : 0;

  // Scroll progress bar
  const progressBar = document.getElementById('scroll-progress');
  if (progressBar) {
    progressBar.style.width = `${scrollPercent}%`;
  }

  // Scroll-to-top button
  const scrollTopBtn = document.getElementById('scroll-top-btn');
  if (scrollTopBtn) {
    scrollTopBtn.classList.toggle('visible', scrollY > CONFIG.scrollTopThreshold);
  }

  // Navbar shadow
  const navbar = document.getElementById('navbar');
  if (navbar) {
    navbar.classList.toggle('scrolled', scrollY > 10);
  }
}

/* ========================================================================
   KEYBOARD SHORTCUTS
   ======================================================================== */

/**
 * Set up keyboard shortcut listeners.
 */
function setupKeyboardListeners() {
  document.addEventListener('keydown', (e) => {
    const modalOpen = document.getElementById('modal-overlay')?.classList.contains('active');
    const searchFocused = document.activeElement === document.getElementById('search-input');
    const overlayOpen = document.getElementById('search-overlay')?.classList.contains('active');

    // Escape
    if (e.key === 'Escape') {
      if (modalOpen) {
        closeModal();
        return;
      }
      if (overlayOpen) {
        closeSearchOverlay();
        return;
      }
      // Blur search if focused
      if (searchFocused) {
        document.getElementById('search-input')?.blur();
        return;
      }
    }

    // "/" — focus search (when modal is closed and search not focused)
    if (e.key === '/' && !modalOpen && !searchFocused) {
      e.preventDefault();
      const isMobile = window.innerWidth <= 640;
      if (isMobile) {
        openSearchOverlay();
      } else {
        document.getElementById('search-input')?.focus();
      }
      return;
    }

    // Ctrl+K or Cmd+K — focus search
    if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      const isMobile = window.innerWidth <= 640;
      if (isMobile) {
        openSearchOverlay();
      } else {
        document.getElementById('search-input')?.focus();
      }
      return;
    }

    // Arrow keys in modal
    if (modalOpen) {
      if (e.key === 'ArrowLeft') {
        navigateModal('prev');
        return;
      }
      if (e.key === 'ArrowRight') {
        navigateModal('next');
        return;
      }

      // Focus trap (Tab handling)
      if (e.key === 'Tab') {
        trapFocus(e);
      }
    }
  });
}

/**
 * Trap focus within the modal for accessibility.
 * @param {KeyboardEvent} e - Keyboard event
 */
function trapFocus(e) {
  const modal = document.getElementById('modal');
  if (!modal) return;

  const focusable = modal.querySelectorAll(
    'button:not([disabled]), [tabindex]:not([tabindex="-1"]), a[href], input, select, textarea'
  );
  if (focusable.length === 0) return;

  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  if (e.shiftKey) {
    // Shift+Tab: if on first, wrap to last
    if (document.activeElement === first) {
      e.preventDefault();
      last.focus();
    }
  } else {
    // Tab: if on last, wrap to first
    if (document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
}

/* ========================================================================
   PWA INSTALL
   ======================================================================== */

/** @type {Event|null} Deferred PWA install prompt */
let deferredPrompt = null;

/**
 * Set up PWA install event listeners.
 */
function setupPWAListeners() {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    const banner = document.getElementById('pwa-banner');
    if (banner) banner.style.display = 'flex';
  });

  const installBtn = document.getElementById('pwa-install-btn');
  const dismissBtn = document.getElementById('pwa-dismiss-btn');

  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) return;

      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`[SeabornGallery] PWA install: ${outcome}`);
      deferredPrompt = null;

      const banner = document.getElementById('pwa-banner');
      if (banner) banner.style.display = 'none';
    });
  }

  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      const banner = document.getElementById('pwa-banner');
      if (banner) banner.style.display = 'none';
      deferredPrompt = null;
    });
  }
}

/* ========================================================================
   BOOTSTRAP
   ======================================================================== */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
