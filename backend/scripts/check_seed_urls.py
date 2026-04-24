"""
Build-time script: HTTP-checks every source URL in seed_data.json
and prints a report of broken links.

Usage:
    python scripts/check_seed_urls.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

SEED_FILE = Path(__file__).parent.parent / "app" / "seed" / "seed_data.json"
TIMEOUT = 10.0


def collect_urls(entries: list[dict]) -> list[str]:
    urls = []
    for entry in entries:
        for qe in entry.get("quantity_events", []):
            if url := qe.get("source_url"):
                urls.append(url)
        for pp in entry.get("price_points", []):
            if url := pp.get("source_url"):
                urls.append(url)
    return list(dict.fromkeys(urls))  # deduplicate, preserve order


def check_urls(urls: list[str]) -> tuple[list[str], list[str]]:
    ok, broken = [], []
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
        for url in urls:
            try:
                resp = client.head(url)
                if resp.status_code < 400:
                    ok.append(url)
                else:
                    broken.append(f"{url}  [HTTP {resp.status_code}]")
            except Exception as exc:
                broken.append(f"{url}  [ERROR: {exc}]")
    return ok, broken


def main() -> None:
    if not SEED_FILE.exists():
        print(f"seed_data.json not found at {SEED_FILE}")
        sys.exit(1)

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    urls = collect_urls(entries)
    print(f"Checking {len(urls)} unique URLs...\n")

    ok, broken = check_urls(urls)

    print(f"✅  OK:     {len(ok)}")
    print(f"❌  Broken: {len(broken)}")

    if broken:
        print("\nBroken URLs:")
        for b in broken:
            print(f"  {b}")
        sys.exit(1)
    else:
        print("\nAll URLs are reachable.")


if __name__ == "__main__":
    main()
