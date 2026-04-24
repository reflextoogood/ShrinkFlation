"""
BLS Public Data API v2 client with SQLite caching.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.models.db import BLSCache

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
CACHE_TTL_HOURS = 24


class BLSUnavailableError(Exception):
    pass


def fetch_bls_series(
    series_id: str,
    start_year: int,
    end_year: int,
    db: Session,
) -> list[dict]:
    """
    Fetch a BLS data series, using the DB cache when available.
    Cache TTL is 24 hours. On API failure, returns cached data if available.
    Raises BLSUnavailableError if API fails and no cache exists.
    """
    cached = db.query(BLSCache).filter(BLSCache.series_id == series_id).first()
    now = datetime.utcnow()

    if cached:
        age = now - cached.fetched_at
        if age < timedelta(hours=CACHE_TTL_HOURS):
            return cached.data

    # Try fetching from BLS API
    try:
        payload = {
            "seriesid": [series_id],
            "startyear": str(start_year),
            "endyear": str(end_year),
        }
        response = httpx.post(BLS_API_URL, json=payload, timeout=15.0)
        response.raise_for_status()
        result = response.json()

        series_data = []
        if result.get("status") == "REQUEST_SUCCEEDED":
            for series in result.get("Results", {}).get("series", []):
                for item in series.get("data", []):
                    series_data.append({
                        "year": int(item["year"]),
                        "period": item.get("period"),
                        "value": float(item["value"]),
                        "series_id": series_id,
                    })

        # Upsert cache
        if cached:
            cached.data = series_data
            cached.fetched_at = now
        else:
            cached = BLSCache(
                series_id=series_id,
                data=series_data,
                fetched_at=now,
                bls_vintage_date=now,
            )
            db.add(cached)
        db.commit()
        return series_data

    except Exception:
        if cached:
            return cached.data
        raise BLSUnavailableError(
            f"BLS API unavailable and no cached data for series {series_id}"
        )
