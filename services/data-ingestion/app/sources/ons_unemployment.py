"""
ONS / NOMIS Labour Force Survey - unemployment rates by age, region, and sector.

We fetch three separate slices and store them all in unemployment_rates,
using "All" as a placeholder for dimensions not being varied
in that slice.
The simulation engine later combines them multiplicatively.
"""

import logging
from io import StringIO
from typing import Any

import pandas as pd
import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..models import UnemploymentRate

logger = logging.getLogger(__name__)

_NOMIS_URL = "https://www.nomisweb.co.uk/api/v01/dataset/NM_17_1.data.csv"

_BASE_PARAMS: dict[str, Any] = {
    "measures": "20100",   # 20100 = percentage value (not counts)
    "sex": "8",  # 8 = total (male + female combined)
    "time": "latest",
    "select": "date_name,geography_name,age_name,industry_name,obs_value",
}

# NOMIS geography codes for Great Britain and its regions
_GB           = "2092957699"
_REGION_CODES = (
    "2013265921,2013265922,2013265923,2013265924,2013265925,"
    "2013265926,2013265927,2013265928,2013265929,2013265930,2013265931"
)

# NM_17_1 industry codes (SIC 2007 major sections)
_ALL_INDUSTRIES = "37748736"
_SECTOR_CODES   = (
    "150994945,150994946,150994947,150994949,150994951,"
    "150994953,150994954,150994956,150994957,150994959,"
    "150994961,150994962,150994963"
)

def _get(extra: dict[str, Any]) -> pd.DataFrame:
    """One NOMIS request, merged with shared base params."""
    response = requests.get(_NOMIS_URL, params=_BASE_PARAMS | extra, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.strip().str.lower()
    return df.dropna(subset=["obs_value"])

def _upsert(db: Session, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    stmt = insert(UnemploymentRate).values(rows)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["period", "sector", "region", "age_band"]
    )
    db.execute(stmt)
    db.commit()
    return len(rows)


def fetch_and_store(db: Session) -> int:
    now    = pd.Timestamp.now()
    period = f"{now.year} Q{now.quarter}"
    total  = 0

    # Slice 1 — by age band, national, all sectors
    logger.info("Fetching unemployment by age band")
    df     = _get({"geography": _GB, "industry": _ALL_INDUSTRIES, "age": "1,2,4,5,6,7,8"})
    total += _upsert(db, [
        {
            "period":   period,
            "sector":   "All",
            "region":   "Great Britain",
            "age_band": row["age_name"],
            "rate_pct": float(row["obs_value"]),
        }
        for _, row in df.iterrows()
    ])

    # Slice 2 — by region, all ages, all sectors
    logger.info("Fetching unemployment by region")
    df     = _get({"geography": _REGION_CODES, "industry": _ALL_INDUSTRIES, "age": "0"})
    total += _upsert(db, [
        {
            "period":   period,
            "sector":   "All",
            "region":   row["geography_name"],
            "age_band": "All",
            "rate_pct": float(row["obs_value"]),
        }
        for _, row in df.iterrows()
    ])

    # Slice 3 — by industry sector, national, all ages
    logger.info("Fetching unemployment by sector")
    df     = _get({"geography": _GB, "industry": _SECTOR_CODES, "age": "0"})
    total += _upsert(db, [
        {
            "period":   period,
            "sector":   row["industry_name"],
            "region":   "Great Britain",
            "age_band": "All",
            "rate_pct": float(row["obs_value"]),
        }
        for _, row in df.iterrows()
    ])

    logger.info("ONS unemployment: wrote %d rows total", total)
    return total


def validate(db: Session) -> None:
    from sqlalchemy import func

    count = db.query(func.count(UnemploymentRate.id)).scalar()
    assert count > 15, f"Expected >15 unemployment rows, got {count}"

    out_of_range = db.query(UnemploymentRate).filter(
        (UnemploymentRate.rate_pct < 0) | (UnemploymentRate.rate_pct > 100)
    ).count()
    assert out_of_range == 0, f"Found {out_of_range} out-of-range rates"

    logger.info("Validation passed: %d ONS unemployment rows", count)