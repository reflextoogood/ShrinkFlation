import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    String, Float, Integer, DateTime, JSON, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.utcnow()


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    severity_score: Mapped[float] = mapped_column(Float, default=0.0)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_deception_gap: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_last_computed: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="brand_rel")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    brand_id: Mapped[str] = mapped_column(String, ForeignKey("brands.id"), nullable=False)
    upc: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    off_id: Mapped[str | None] = mapped_column(String, nullable=True)
    verification_status: Mapped[str] = mapped_column(String, default="verified")
    off_last_updated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    brand_rel: Mapped["Brand"] = relationship("Brand", back_populates="products")
    shrinkflation_events: Mapped[list["ShrinkflationEvent"]] = relationship(
        "ShrinkflationEvent", back_populates="product"
    )
    price_points: Mapped[list["PricePoint"]] = relationship(
        "PricePoint", back_populates="product"
    )


class ShrinkflationEvent(Base):
    __tablename__ = "shrinkflation_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity_value: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    product: Mapped["Product"] = relationship("Product", back_populates="shrinkflation_events")


class PricePoint(Base):
    __tablename__ = "price_points"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    bls_series_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    product: Mapped["Product"] = relationship("Product", back_populates="price_points")


class CrowdsourcedReport(Base):
    __tablename__ = "crowdsourced_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    submission_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String, nullable=False)
    upc: Mapped[str | None] = mapped_column(String, nullable=True)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    before_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    after_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String, nullable=False)
    change_year: Mapped[int] = mapped_column(Integer, nullable=False)
    change_month: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    verification_status: Mapped[str] = mapped_column(String, default="unverified")
    confirming_source: Mapped[str | None] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BLSCache(Base):
    __tablename__ = "bls_cache"

    series_id: Mapped[str] = mapped_column(String, primary_key=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[Any] = mapped_column(JSON, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bls_vintage_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
