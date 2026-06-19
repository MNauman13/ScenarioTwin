"""
Data ingestion entry point — run as a one-shot script via GitHub Actions,
not a long-running server.
"""
import logging
from .database import engine, SessionLocal, Base
from . import models  # noqa: F401 — registers all tables with Base.metadata before create_all
from .sources import market_returns, boe_rates

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Creating tables if they don't exist")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        logger.info("=== Market returns ===")
        results = market_returns.fetch_and_store(db)
        market_returns.validate(db)
        logger.info("Market returns done: %s", results)

        logger.info("=== Interest rates ===")
        boe_results = boe_rates.fetch_and_store(db)
        boe_rates.validate(db)
        logger.info("Interest rates done: %d rows", boe_results)


if __name__ == "__main__":
    main()
