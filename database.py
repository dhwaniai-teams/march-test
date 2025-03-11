import asyncpg
import os
import logging

DATABASE_URL = "postgresql://postgres:dhwaniai@localhost/dhwani_db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db():
    """Establishes database connection."""
    return await asyncpg.connect(DATABASE_URL)

async def fetch_dynamic_details(intent):
    """Fetches details dynamically based on intent from the database."""
    db = await get_db()
    try:
        table_info = await db.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'loans'")
        columns = [row["column_name"] for row in table_info]

        query_str = f"SELECT {', '.join(columns)} FROM loans WHERE loan_type ILIKE $1"
        result = await db.fetchrow(query_str, f"%{intent}%")

        return dict(result) if result else None
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None
    finally:
        await db.close()
