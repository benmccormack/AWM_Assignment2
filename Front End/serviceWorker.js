const pubFinder = "Pub-Finder";
const assets = [
    "/",
    "/index.html",
    "/register.html",
    "/map.html",
    "/assets/css/style.css",
    "/assets/scripts/index.js",
]

self.addEventListener("install", installEvent => {
  installEvent.waitUntil(
    caches.open(pubFinder).then(cache => {
      cache.addAll(assets)
    })
  )
})

self.addEventListener("fetch", fetchEvent => {
    fetchEvent.respondWith(
      caches.match(fetchEvent.request).then(res => {
        return res || fetch(fetchEvent.request)
      })
    )
  })

