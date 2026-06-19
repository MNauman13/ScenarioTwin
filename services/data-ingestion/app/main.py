"""
Data ingestion entry point — run as a one-shot script via GitHub Actions,
not a long-running server.
"""
import logging
from .database import engine, SessionLocal, Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Creating tables if they don't exist")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from .sources import market_returns
        logger.info("=== Market returns ===")
        results = market_returns.fetch_and_store(db)
        market_returns.validate(db)
        logger.info("Market returns done: %s", results)
    finally:
        db.close()


if __name__ == "__main__":
    main()
