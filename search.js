/**
 * SeabornGallery — Search Module
 * ================================
 * Provides fuzzy search, scoring, suggestions, highlighting, and search history.
 * Exposes window.MatplotSearch for use by app.js.
 *
 * This file must be loaded BEFORE app.js.
 */

(function () {
  'use strict';

  /* ======================================================================
     CONSTANTS
     ====================================================================== */

  const MAX_QUERY_LENGTH = 100;
  const FUZZY_MIN_CHARS = 4;

  /* ======================================================================
     CACHE
     ====================================================================== */

  /**
   * Cache for normalized plot data to avoid re-computing on every search.
   * Maps plot id -> { name, tags[], difficulty, idStr }
   * @type {Map<number, Object>|null}
   */
  let normalizedCache = null;

  /**
   * Build or retrieve the normalized cache for a given plots array.
   * @param {Array} plots - Array of plot objects
   * @returns {Map<number, Object>} Normalized cache
   */
  function getCache(plots) {
    // Rebuild cache if plots array changed (simple length check + first id check)
    if (
      normalizedCache &&
      normalizedCache._length === plots.length &&
      normalizedCache._firstId === (plots[0]?.id ?? null)
    ) {
      return normalizedCache;
    }

    const cache = new Map();
    cache._length = plots.length;
    cache._firstId = plots[0]?.id ?? null;

    plots.forEach((plot) => {
      cache.set(plot.id, {
        name: normalize(plot.name || ''),
        nameWords: normalize(plot.name || '').split(/\s+/).filter(Boolean),
        tags: (plot.tags || []).map((t) => normalize(t)),
        tagsRaw: plot.tags || [],
        difficulty: normalize(plot.difficulty || ''),
        idStr: String(plot.id),
      });
    });

    normalizedCache = cache;
    return cache;
  }

  /* ======================================================================
     TEXT UTILITIES
     ====================================================================== */

  /**
   * Normalize a string: lowercase, trim, remove special chars, collapse whitespace.
   * @param {string} str - Input string
   * @returns {string} Normalized string
   */
  function normalize(str) {
    return String(str)
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, ' ');
  }

  /**
   * Escape HTML special characters.
   * @param {string} str - Raw string
   * @returns {string} Escaped string
   */
  function sanitizeHTML(str) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' };
    return String(str).replace(/[&<>"']/g, (c) => map[c]);
  }

  /**
   * Compute the Levenshtein edit distance between two strings.
   * Dynamic programming implementation.
   * @param {string} a - First string
   * @param {string} b - Second string
   * @returns {number} Edit distance
   */
  function levenshtein(a, b) {
    const m = a.length;
    const n = b.length;

    // Quick exits
    if (m === 0) return n;
    if (n === 0) return m;
    if (a === b) return 0;

    // Create DP matrix
    const dp = [];
    for (let i = 0; i <= m; i++) {
      dp[i] = [i];
    }
    for (let j = 0; j <= n; j++) {
      dp[0][j] = j;
    }

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,       // deletion
          dp[i][j - 1] + 1,       // insertion
          dp[i - 1][j - 1] + cost // substitution
        );
      }
    }

    return dp[m][n];
  }

  /* ======================================================================
     SCORING
     ====================================================================== */

  /**
   * Score a single plot against an array of search words.
   * All words must match — if any word scores 0, total score is 0.
   *
   * @param {Object} plot - Plot data object
   * @param {string[]} words - Normalized search words
   * @param {Map} cache - Normalized cache
   * @returns {number} Total score (0 = no match)
   */
  function scorePlot(plot, words, cache) {
    const cached = cache.get(plot.id);
    if (!cached) return 0;

    let totalScore = 0;

    for (const word of words) {
      let wordScore = 0;

      // --- Name matching ---
      const nameNorm = cached.name;
      const nameWords = cached.nameWords;

      // Exact word in name
      if (nameWords.includes(word)) {
        wordScore += 100;
      }
      // Partial match in name
      else if (nameNorm.includes(word)) {
        wordScore += 60;
        // Prefix bonus: name starts with word
        if (nameNorm.startsWith(word)) {
          wordScore += 30;
        }
      }
      // Fuzzy match in name words (only for words >= FUZZY_MIN_CHARS)
      else if (word.length >= FUZZY_MIN_CHARS) {
        const tolerance = Math.floor(word.length / 4);
        for (const nw of nameWords) {
          if (nw.length >= FUZZY_MIN_CHARS) {
            const dist = levenshtein(word, nw);
            if (dist <= tolerance) {
              wordScore += 40;
              break;
            }
          }
        }
      }

      // Full name exact match bonus
      if (nameNorm === word) {
        wordScore += 50;
      }

      // --- Tag matching ---
      const tags = cached.tags;
      let tagMatched = false;

      for (const tag of tags) {
        if (tag === word) {
          wordScore += 80;
          tagMatched = true;
          break;
        }
        if (tag.includes(word)) {
          wordScore += 50;
          tagMatched = true;
          break;
        }
      }

      // --- Difficulty matching ---
      if (cached.difficulty === word) {
        wordScore += 70;
      } else if (cached.difficulty.includes(word)) {
        wordScore += 40;
      }

      // --- ID matching ---
      if (cached.idStr === word) {
        wordScore += 90;
      } else if (cached.idStr.includes(word)) {
        wordScore += 45;
      }

      // If this word has no matches at all, total is 0 (AND logic)
      if (wordScore === 0) {
        return 0;
      }

      totalScore += wordScore;
    }

    return totalScore;
  }

  /* ======================================================================
     PUBLIC API
     ====================================================================== */

  /**
   * Filter and rank plots by search query.
   *
   * @param {Array} plots - Array of plot objects
   * @param {string} query - Search query string
   * @returns {Array} Filtered and sorted plots
   */
  function filter(plots, query) {
    if (!query || !query.trim()) return plots;

    // Truncate query
    const trimmed = query.slice(0, MAX_QUERY_LENGTH).trim();
    if (!trimmed) return plots;

    const normalized = normalize(trimmed);
    const words = normalized.split(/\s+/).filter(Boolean);
    if (words.length === 0) return plots;

    // Track search history
    trackSearch(trimmed);

    // Build/get cache
    const cache = getCache(plots);

    // Score all plots
    const scored = [];
    for (const plot of plots) {
      const score = scorePlot(plot, words, cache);
      if (score > 0) {
        scored.push({ plot, score });
      }
    }

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    return scored.map((s) => s.plot);
  }

  /**
   * Get search suggestions based on a partial query.
   *
   * @param {Array} plots - Array of plot objects
   * @param {string} query - Partial search query
   * @param {number} maxSuggestions - Maximum suggestions to return
   * @returns {string[]} Array of suggestion strings
   */
  function getSuggestions(plots, query, maxSuggestions = 5) {
    if (!query || !query.trim()) return [];

    const q = normalize(query);
    if (!q) return [];

    // Collect candidates: plot names, unique tags, difficulty values
    const candidates = new Set();

    plots.forEach((plot) => {
      if (plot.name) candidates.add(plot.name);
      if (plot.tags) plot.tags.forEach((t) => candidates.add(t));
      if (plot.difficulty) candidates.add(plot.difficulty);
    });

    const all = [...candidates];

    // Items starting with query first, then items containing query
    const startsWithList = [];
    const containsList = [];

    all.forEach((item) => {
      const normalized = normalize(item);
      if (normalized.startsWith(q)) {
        startsWithList.push(item);
      } else if (normalized.includes(q)) {
        containsList.push(item);
      }
    });

    // Combine, deduplicate, limit
    const result = [];
    const seen = new Set();

    for (const item of [...startsWithList, ...containsList]) {
      if (!seen.has(item.toLowerCase())) {
        seen.add(item.toLowerCase());
        result.push(item);
        if (result.length >= maxSuggestions) break;
      }
    }

    return result;
  }

  /**
   * Return HTML string with matching substrings wrapped in <mark> tags.
   *
   * @param {string} text - Original text
   * @param {string} query - Search query
   * @returns {string} HTML string with highlights
   */
  function getHighlightedText(text, query) {
    if (!query || !query.trim() || !text) return sanitizeHTML(text);

    const q = query.trim();
    const escapedQ = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedQ})`, 'gi');

    const parts = text.split(regex);
    let html = '';

    parts.forEach((part) => {
      if (regex.test(part)) {
        html += `<mark>${sanitizeHTML(part)}</mark>`;
        regex.lastIndex = 0; // reset regex state
      } else {
        html += sanitizeHTML(part);
      }
    });

    return html;
  }

  /* ======================================================================
     SEARCH HISTORY
     ====================================================================== */

  /** @type {Map<string, number>} Search term -> count */
  const searchHistory = new Map();

  /**
   * Track a search term.
   * @param {string} term - Search term
   */
  function trackSearch(term) {
    const key = term.toLowerCase().trim();
    if (key.length < 2) return;
    searchHistory.set(key, (searchHistory.get(key) || 0) + 1);
  }

  /**
   * Get the top N most searched terms.
   * @param {number} n - Number of top terms to return
   * @returns {string[]} Array of top search terms
   */
  function getTopSearches(n = 5) {
    const entries = [...searchHistory.entries()];
    entries.sort((a, b) => b[1] - a[1]);
    return entries.slice(0, n).map((e) => e[0]);
  }

  /* ======================================================================
     EXPOSE PUBLIC API
     ====================================================================== */

  window.MatplotSearch = {
    filter,
    getSuggestions,
    getHighlightedText,
    searchHistory,
    getTopSearches,
  };

})();
