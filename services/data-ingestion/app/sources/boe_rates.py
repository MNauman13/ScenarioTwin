import logging
from io import StringIO

import pandas as pd
import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..models import InterestRate

logger = logging.getLogger(__name__)

_BOE_URL = (
    "https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp"
    "?Travel=NIxRSxSUx&FromSeries=1&ToSeries=50"
    "&DAT=RNG&FD=1&FM=Jan&FY=1975&TD=31&TM=Dec&TY=2030"
    "&VFD=Y&html.x=66&html.y=26&C=IUDBEDR&Filter=N&csv.x=46&csv.y=9"
)

def fetch_and_store(db: Session) -> int:
    logger.info("Fetching BoE base rate history")

    response = requests.get(_BOE_URL, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.strip()

    # BoE uses "." to indicate missing values in older series - drop them
    df = df[df["IUDBEDR"].notna()]
    df = df[df["IUDBEDR"].astype(str).str.strip() != "."]

    df["date"] = pd.to_datetime(df["Date"].str.strip(), format="%d %b %Y").dt.date
    df["rate_pct"] = df["IUDBEDR"].astype(float)
    df["source"] = "BoE"

    rows = df[["date", "rate_pct", "source"]].to_dict(orient="records")

    stmt = insert(InterestRate).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["date"])
    db.execute(stmt)
    db.commit()

    logger.info("BoE rates: wrote %d rows", len(rows))
    return len(rows)

def validate(db: Session) -> None:
    from sqlalchemy import func

    count = db.query(func.count(InterestRate.id)).scalar()
    assert count > 100, f"Expected >100 rate rows, got {count}"

    out_of_range = db.query(InterestRate).filter(
        (InterestRate.rate_pct < 0) | (InterestRate.rate_pct > 20)
    ).count()
    assert out_of_range == 0, f"Found {out_of_range} out-of-range interest rates"

    logger.info("Validation passed: %d BoE rate rows", count)
