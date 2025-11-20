// Simple in-memory cache middleware
// For production, use Redis

const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

const cacheMiddleware = (duration = CACHE_TTL) => {
  return (req, res, next) => {
    if (req.method !== 'GET') {
      return next();
    }

    const key = `__express__${req.originalUrl || req.url}`;
    const cachedResponse = cache.get(key);

    if (cachedResponse && cachedResponse.expires > Date.now()) {
      return res.json(cachedResponse.data);
    }

    // Override res.json to cache the response
    const originalJson = res.json.bind(res);
    res.json = (data) => {
      cache.set(key, {
        data,
        expires: Date.now() + duration
      });
      return originalJson(data);
    };

    next();
  };
};

// Clear cache for specific pattern
const clearCache = (pattern) => {
  for (const key of cache.keys()) {
    if (key.includes(pattern)) {
      cache.delete(key);
    }
  }
};

// Clear all cache
const clearAllCache = () => {
  cache.clear();
};

// Auto-cleanup old cache entries every 10 minutes
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of cache.entries()) {
    if (value.expires < now) {
      cache.delete(key);
    }
  }
}, 10 * 60 * 1000);

module.exports = { cacheMiddleware, clearCache, clearAllCache };
