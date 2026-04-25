"""
Open Food Facts API v2 client with in-memory TTL cache.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

OFF_BASE = "https://world.openfoodfacts.org"
CACHE_TTL = 3600  # 1 hour in seconds


class OFFUnavailableError(Exception):
    pass


_cache: dict[str, tuple[float, object]] = {}


def _cache_get(key: str) -> Optional[object]:
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < CACHE_TTL:
        return entry[1]
    return None


def _cache_set(key: str, value: object) -> None:
    _cache[key] = (time.time(), value)


def search_by_name(query: str) -> list[dict]:
    """Search OFF by product name. Returns list of product dicts."""
    key = f"name:{query}"
    cached = _cache_get(key)
    if cached is not None:
        return cached  # type: ignore

    try:
        url = f"{OFF_BASE}/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 20,
        }
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        products = resp.json().get("products", [])
        _cache_set(key, products)
        return products
    except Exception as exc:
        raise OFFUnavailableError(f"OFF API unavailable: {exc}") from exc


def search_by_upc(upc: str) -> Optional[dict]:
    """Look up a product by UPC/barcode. Returns product dict or None."""
    key = f"upc:{upc}"
    cached = _cache_get(key)
    if cached is not None:
        return cached  # type: ignore

    try:
        url = f"{OFF_BASE}/api/v2/product/{upc}.json"
        resp = httpx.get(url, timeout=10.0)
        if resp.status_code == 404:
            _cache_set(key, None)
            return None
        resp.raise_for_status()
        data = resp.json()
        product = data.get("product") if data.get("status") == 1 else None
        _cache_set(key, product)
        return product
    except Exception as exc:
        raise OFFUnavailableError(f"OFF API unavailable: {exc}") from exc
