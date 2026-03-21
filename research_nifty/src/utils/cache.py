from __future__ import annotations

from diskcache import Cache


class TTLCache:
    def __init__(self, path: str = "data/cache") -> None:
        self.cache = Cache(path)

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value, ttl: int | None = None) -> None:
        self.cache.set(key, value, expire=ttl)
