from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, UniqueConstraint
from .database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class MarketReturn(Base):
    __tablename__ = "market_returns"

    id           = Column(Integer, primary_key=True)
    date         = Column(Date, nullable=False)
    ticker       = Column(String(20), nullable=False)   # "^FTSE", "^GSPC", "^VUKE.L"
    price_close  = Column(Float, nullable=False)
    daily_return = Column(Float, nullable=False)        # log return, not simple return
    created_at   = Column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (UniqueConstraint("date", "ticker"),)


class InterestRate(Base):
    __tablename__ = "interest_rates"

    id         = Column(Integer, primary_key=True)
    date       = Column(Date, nullable=False, unique=True)
    rate_pct   = Column(Float, nullable=False)          # e.g. 5.25 for 5.25%
    source     = Column(String(50), default="BoE")
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class UnemploymentRate(Base):
    __tablename__ = "unemployment_rates"

    id         = Column(Integer, primary_key=True)
    period     = Column(String(20), nullable=False)     # "2024 Q1"
    sector     = Column(String(100), nullable=False)    # "Professional services"
    region     = Column(String(100), nullable=False)    # "London"
    age_band   = Column(String(50), nullable=False)     # "25-34"
    rate_pct   = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (UniqueConstraint("period", "sector", "region", "age_band"),)