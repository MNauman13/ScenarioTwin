from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class MarketReturn(Base):
    __tablename__ = "market_returns"

    id:           Mapped[int]      = mapped_column(primary_key=True)
    date:         Mapped[date]
    ticker:       Mapped[str]      = mapped_column(String(20))
    price_close:  Mapped[float]
    daily_return: Mapped[float]
    created_at:   Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("date", "ticker"),)


class InterestRate(Base):
    __tablename__ = "interest_rates"

    id:         Mapped[int]      = mapped_column(primary_key=True)
    date:       Mapped[date]     = mapped_column(unique=True)
    rate_pct:   Mapped[float]
    source:     Mapped[str]      = mapped_column(String(50), default="BoE")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )


class UnemploymentRate(Base):
    __tablename__ = "unemployment_rates"

    id:         Mapped[int]      = mapped_column(primary_key=True)
    period:     Mapped[str]      = mapped_column(String(20))
    sector:     Mapped[str]      = mapped_column(String(100))
    region:     Mapped[str]      = mapped_column(String(100))
    age_band:   Mapped[str]      = mapped_column(String(50))
    rate_pct:   Mapped[float]
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("period", "sector", "region", "age_band"),)