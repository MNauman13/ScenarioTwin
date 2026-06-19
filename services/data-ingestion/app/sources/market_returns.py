import logging
import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from ..models import MarketReturn

logger = logging.getLogger(__name__)

TICKERS = {
    "^FTSE": "FTSE 100",
    "^GSPC": "S&P 500",
    "^VUKE.L": "Vanguard FTSE UK ETF",  # good proxy for UK equity returns
}

START_DATE = "1990-01-01"  # 35 years of data which is enough for multiple regime cycles

def fetch_and_store(db: Session) -> dict[str, int]:
    """
    Download historical daily closes for each ticker,
    compute log returns, upsert into market_returns.
    Returns a dict of {ticker: rows_written}.
    """
    results = {}

    for ticker, label in TICKERS.items():
        logger.info(f"Fetching {ticker} ({label})")
        raw: pd.DataFrame = yf.download(
            ticker,
            start=START_DATE,
            auto_adjust=True,
            progress=False
        )

        if raw.empty:
            logger.warning(f"No data returned for {ticker} - skipping")
            results[ticker] = 0
            continue

        # yfinance returns a MultiIndex when downloading one ticker - flatten it
        raw.columns = raw.columns.get_level_values(0)

        closes = raw["Close"].dropna()
        log_returns = np.log(closes / closes.shift(1)).dropna()

        rows = [
            {
                "date":  date.date(),
                "ticker": ticker,
                "price_close": float(closes.loc[date]),
                "daily_return": float(log_returns.loc[date]),
            }
            for date in log_returns.index
        ]

        # Upsert: insert rows, but if (date, ticker) already exists, do nothing
        stmt = insert(MarketReturn).values(rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=["date", "ticker"])
        db.execute(stmt)
        db.commit()

        results[ticker] = len(rows)
        logger.info(f"{ticker}: wrote {len(rows)} rows")

    return results

def validate(db: Session) -> None:
    """
    Sanity check: FTSE 100 should have data going back to at least 2000
    and returns should be within a plausible range (no $90%+ daily moves)
    """
    from sqlalchemy import func

    count = db.query(func.count(MarketReturn.id)).filter(
        MarketReturn.ticker == "^FTSE"
    ).scalar()
    assert count > 5000, f"Expected >5000 FTSE rows, got {count}"

    extreme = db.query(MarketReturn).filter(
        MarketReturn.ticker == "^FTSE",
        MarketReturn.daily_return > 0.25  # >28% daily move = something is wrong
    ).count()
    assert extreme == 0, f"Found {extreme} suspiciously large daily returns"

    logger.info("Validation passed: %d FTSE rows, no extreme outliers", count)