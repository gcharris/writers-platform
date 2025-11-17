"""Query result caching system."""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class QueryCache:
    """LRU cache for knowledge query results."""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """Initialize query cache.

        Args:
            max_size: Maximum cache entries
            ttl: Time-to-live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._hits = 0
        self._misses = 0
        logger.info(f"Initialized query cache (max_size={max_size}, ttl={ttl}s)")

    def _hash_query(self, query: str, params: Optional[Dict] = None) -> str:
        """Generate hash key for query.

        Args:
            query: Query text
            params: Additional parameters

        Returns:
            Hash key
        """
        data = {"query": query, "params": params or {}}
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get(self, query: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get cached result.

        Args:
            query: Query text
            params: Additional parameters

        Returns:
            Cached result or None if not found/expired
        """
        key = self._hash_query(query, params)

        if key not in self._cache:
            self._misses += 1
            return None

        # Check TTL
        if time.time() - self._access_times[key] > self.ttl:
            self._evict(key)
            self._misses += 1
            return None

        # Update access time
        self._access_times[key] = time.time()
        self._hits += 1

        logger.debug(f"Cache hit for query: {query[:50]}...")
        return self._cache[key]

    def set(self, query: str, result: Any, params: Optional[Dict] = None) -> None:
        """Cache a query result.

        Args:
            query: Query text
            result: Result to cache
            params: Additional parameters
        """
        key = self._hash_query(query, params)

        # Evict oldest if at max size
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        self._cache[key] = result
        self._access_times[key] = time.time()

        logger.debug(f"Cached result for query: {query[:50]}...")

    def _evict(self, key: str) -> None:
        """Evict specific key."""
        if key in self._cache:
            del self._cache[key]
            del self._access_times[key]

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._access_times:
            return

        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        self._evict(lru_key)
        logger.debug(f"Evicted LRU cache entry: {lru_key[:16]}...")

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()
        logger.info("Cleared query cache")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "ttl": self.ttl,
        }
