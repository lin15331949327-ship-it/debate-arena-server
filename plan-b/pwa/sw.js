const CACHE = 'debate-arena-v2';
const PRELOAD = [
  '/', '/index.html', '/socket.io.min.js',
  '/pwa-liquid-glass.html', '/pwa-river-of-light.html',
  '/pwa-epistolary.html', '/pwa-frost-white.html', '/pwa-anime-vn.html',
  '/manifest-liquid-glass.json', '/manifest-river-of-light.json',
  '/manifest-epistolary.json', '/manifest-frost-white.json', '/manifest-anime-vn.json',
  '/icon-192.png', '/icon-512.png'
];

self.addEventListener('install', e => {
  // Purge old cache, don't pre-cache (let fetch populate)
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', e => {
  // Network-first for HTML pages, cache for static assets
  const url = new URL(e.request.url);
  if (url.pathname.endsWith('.html') || url.pathname === '/') {
    e.respondWith(
      fetch(e.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE).then(cache => cache.put(e.request, clone));
        return response;
      }).catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE).then(cache => cache.put(e.request, clone));
        return response;
      }))
    );
  }
});
