#app/api/rag/rag_model.py
import logging
from services.search_service import create_text_index, retrieve_articles

logger = logging.getLogger(__name__)

# Model layer remains clean and focuses on initiating the model-related functionality
def ensure_text_index():
    """
    Ensures the necessary text index exists for efficient searching.
    """
    try:
        create_text_index()
    except Exception as e:
        logger.error(f"Failed to ensure text index: {str(e)}")
