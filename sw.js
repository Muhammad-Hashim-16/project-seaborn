/**
 * SeabornGallery — Service Worker
 * ================================
 * Provides offline support and caching for the SeabornGallery PWA.
 *
 * Strategy:
 *   - Cache First for figure images (figures/ folder)
 *   - Network First for all other requests
 *
 * If deploying to Vercel, the sw.js file in the project root will be
 * served at the domain root and the scope will be correct automatically.
 * No changes needed for Vercel deployment.
 */

const CACHE_NAME = 'seaborngallery-v1';

/**
 * Core assets to cache on install.
 * These are the essential files needed for the app shell.
 */
const CORE_ASSETS = [
  './index.html',
  './about.html',
  './style.css',
  './app.js',
  './search.js',
  './data.json',
  './manifest.json',
];

// ---------------------------------------------------------------------------
// Install event — pre-cache core assets
// ---------------------------------------------------------------------------
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Pre-caching core assets');
        return cache.addAll(CORE_ASSETS);
      })
      .then(() => {
        console.log('[SW] Core assets cached successfully');
      })
      .catch((err) => {
        console.warn('[SW] Failed to cache some core assets:', err);
      })
  );
});

// ---------------------------------------------------------------------------
// Activate event — clean up old caches
// ---------------------------------------------------------------------------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => {
              console.log(`[SW] Deleting old cache: ${name}`);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Activated and old caches cleared');
      })
  );
});

// ---------------------------------------------------------------------------
// Fetch event — routing strategy
// ---------------------------------------------------------------------------
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Cache First strategy for figure images
  if (url.pathname.includes('/figures/')) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // Network First strategy for all other requests
  event.respondWith(networkFirst(event.request));
});

// ---------------------------------------------------------------------------
// Message event — allow skip waiting
// ---------------------------------------------------------------------------
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// ---------------------------------------------------------------------------
// Cache First strategy
// ---------------------------------------------------------------------------
/**
 * Try the cache first. If the resource is not in the cache,
 * fetch it from the network, add it to the cache, and return it.
 *
 * @param {Request} request - The fetch request
 * @returns {Promise<Response>} The cached or fetched response
 */
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Not in cache — fetch from network
    const networkResponse = await fetch(request);

    // Only cache successful responses
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.warn('[SW] Cache-first fetch failed:', error);

    // Return a fallback offline response for images
    return new Response('', {
      status: 503,
      statusText: 'Service Unavailable',
    });
  }
}

// ---------------------------------------------------------------------------
// Network First strategy
// ---------------------------------------------------------------------------
/**
 * Try the network first. If the network fails, fall back to the cache.
 *
 * @param {Request} request - The fetch request
 * @returns {Promise<Response>} The network or cached response
 */
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);

    // Cache successful responses for offline use
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Network failed — try the cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('[SW] Serving from cache (offline):', request.url);
      return cachedResponse;
    }

    // Nothing in cache either
    console.warn('[SW] No cache available for:', request.url);
    return new Response('Offline — resource not available', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' },
    });
  }
}
