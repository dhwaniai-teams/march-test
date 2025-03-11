import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_intent(user_text):
    """Extracts loan-related keywords dynamically."""
    keywords = ["home loan", "car loan", "personal loan", "education loan"]

    for keyword in keywords:
        if re.search(rf"\b{keyword}\b", user_text, re.IGNORECASE):
            return keyword

    logger.warning(f"No matching intent found for: {user_text}")
    return None  # No relevant keyword found
