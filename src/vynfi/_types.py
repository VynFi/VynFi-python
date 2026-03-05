"""Pydantic models for VynFi API responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

# ── Jobs ──


class JobLinks(BaseModel):
    self_link: str = Field(alias="self")
    stream: str = ""
    cancel: str = ""
    download: str = ""


class JobProgress(BaseModel):
    percent: int = 0
    rows_generated: int = 0
    rows_total: int = 0


class Job(BaseModel):
    id: str
    status: str
    tables: Any = None
    format: str = "json"
    credits_reserved: int = 0
    credits_used: int = 0
    sector_slug: str = ""
    progress: JobProgress | None = None
    output_path: str | None = None
    error: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class SubmitJobResponse(BaseModel):
    id: str
    status: str
    credits_reserved: int = 0
    estimated_duration_seconds: int = 0
    links: JobLinks | None = None


class JobList(BaseModel):
    jobs: list[Job]
    has_more: bool = False
    next_cursor: str | None = None


# ── Catalog / Sectors ──


class Column(BaseModel):
    name: str
    data_type: str = ""
    description: str = ""
    nullable: bool = False


class TableDef(BaseModel):
    name: str
    description: str = ""
    base_rate: float = 1.0
    columns: list[Column] = Field(default_factory=list)


class Sector(BaseModel):
    slug: str
    name: str
    description: str = ""
    icon: str = ""
    multiplier: float = 1.0
    quality_score: float = 0.0
    popularity: int = 0
    tables: list[TableDef] = Field(default_factory=list)


class SectorSummary(BaseModel):
    slug: str
    name: str
    description: str = ""
    icon: str = ""
    table_count: int = 0


class CatalogItem(BaseModel):
    sector: str = ""
    profile: str = ""
    name: str = ""
    description: str = ""
    source: str = ""


class Fingerprint(BaseModel):
    sector: str = ""
    profile: str = ""
    name: str = ""
    description: str = ""
    source: str = ""
    columns: list[Column] = Field(default_factory=list)


# ── Usage ──


class UsageSummary(BaseModel):
    balance: int = 0
    total_used: int = 0
    total_reserved: int = 0
    total_refunded: int = 0
    burn_rate: float = 0.0
    period_days: int = 30


class DailyUsage(BaseModel):
    date: date
    credits: int = 0


class DailyUsageResponse(BaseModel):
    daily: list[DailyUsage] = Field(default_factory=list)
    by_table: dict[str, int] = Field(default_factory=dict)


# ── API Keys ──


class ApiKey(BaseModel):
    id: str
    name: str
    prefix: str = ""
    scopes: list[str] = Field(default_factory=list)
    status: str = "active"
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime | None = None


class ApiKeyCreated(BaseModel):
    id: str
    name: str
    key: str
    prefix: str = ""
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    created_at: datetime | None = None


# ── Quality ──


class QualityScore(BaseModel):
    id: str
    job_id: str
    table_type: str = ""
    rows: int = 0
    overall_score: float = 0.0
    benford_score: float = 0.0
    correlation_score: float = 0.0
    distribution_score: float = 0.0
    created_at: datetime | None = None


class DailyQuality(BaseModel):
    date: date
    score: float = 0.0


# ── Webhooks ──


class Webhook(BaseModel):
    id: str
    url: str
    events: list[str] = Field(default_factory=list)
    status: str = "active"
    secret: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WebhookCreated(BaseModel):
    id: str
    url: str
    events: list[str] = Field(default_factory=list)
    secret: str = ""
    created_at: datetime | None = None


# ── Billing ──


class Subscription(BaseModel):
    tier: str = "free"
    status: str = "active"
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False


class Invoice(BaseModel):
    id: str = ""
    amount: int = 0
    currency: str = "usd"
    status: str = ""
    created_at: datetime | None = None
    pdf_url: str | None = None


class PaymentMethod(BaseModel):
    type: str = ""
    brand: str = ""
    last4: str = ""
    exp_month: int = 0
    exp_year: int = 0
