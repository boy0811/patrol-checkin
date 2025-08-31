self.addEventListener("install", event => {
  event.waitUntil(
    caches.open("checkin-cache-v1").then(cache => {
      return cache.addAll([
        "/",
        "/member_checkin_home",
        "/static/manifest.json",
        "/static/logo/logo.png"
      ]);
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
