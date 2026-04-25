"""
Seed data loader — upserts products, brands, shrinkflation events, and price points
from seed_data.json into SQLite on app startup.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.db import Brand, Product, ShrinkflationEvent, PricePoint

SEED_FILE = Path(__file__).parent / "seed_data.json"


def _get_or_create_brand(db: Session, name: str) -> Brand:
    brand = db.query(Brand).filter(Brand.name == name).first()
    if not brand:
        brand = Brand(id=str(uuid.uuid4()), name=name)
        db.add(brand)
        db.flush()
    return brand


def load_seed_data(db: Session) -> None:
    """
    Read seed_data.json and upsert all products, brands, events, and price points.
    Safe to call multiple times — skips existing products by UPC.
    """
    if not SEED_FILE.exists():
        print(f"[seed] seed_data.json not found at {SEED_FILE}, skipping.")
        return

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    loaded = 0
    for entry in entries:
        upc = entry.get("upc")

        # Skip if already loaded
        existing = db.query(Product).filter(Product.upc == upc).first() if upc else None
        if existing:
            continue

        brand = _get_or_create_brand(db, entry["brand"])

        product = Product(
            id=str(uuid.uuid4()),
            name=entry["product_name"],
            brand_id=brand.id,
            upc=upc,
            category=entry.get("category"),
            verification_status="verified",
            off_last_updated=datetime.utcnow(),
        )
        db.add(product)
        db.flush()

        for qe in entry.get("quantity_events", []):
            event = ShrinkflationEvent(
                id=str(uuid.uuid4()),
                product_id=product.id,
                year=qe["year"],
                quantity_value=qe["quantity_value"],
                quantity_unit=qe["quantity_unit"],
                source_type="seed",
                source_url=qe.get("source_url"),
            )
            db.add(event)

        for pp in entry.get("price_points", []):
            price_point = PricePoint(
                id=str(uuid.uuid4()),
                product_id=product.id,
                year=pp["year"],
                price_usd=pp["price_usd"],
                source_type="seed",
                source_url=pp.get("source_url"),
            )
            db.add(price_point)

        loaded += 1

    db.commit()
    print(f"[seed] Loaded {loaded} new products from seed_data.json.")
