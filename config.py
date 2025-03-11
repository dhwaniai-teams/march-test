import os
import logging

# Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dhwaniai@localhost/dhwani_db")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key")

# Logging Setup
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger
