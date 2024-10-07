#app/services/search_service.py
from pymongo.errors import PyMongoError
from utils.common import normalize_text, get_mongo_collection
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Vietnamese stopwords 
STOPWORDS_VIETNAMESE = {"và", "là", "của", "cái", "những", "các", "với", "vào", "được", "đến", "từ", "có", "trong", "để", "thì"}

def create_text_index():
    """
    Ensures that a text index on the 'title' and 'content' fields of the articles collection exists,
    with higher priority given to the 'title'.
    """
    try:
        articles_collection = get_mongo_collection('newsdb', 'articles')

        existing_indexes = articles_collection.index_information()
        index_exists = False

        # Check if the index already exists
        for index in existing_indexes.values():
            if index.get('key', []) == [('title', 'text'), ('content', 'text')]:
                index_exists = True
                break

        if not index_exists:
            # Create the text index if it doesn't exist
            articles_collection.create_index(
                [("title", "text"), ("content", "text")],
                weights={"title": 20, "content": 5},  # Give higher priority to the title
                name="title_content_text_index",
                default_language="none"
            )
            logger.info("Text index created on 'title' and 'content'.")
        else:
            logger.info("Text index on 'title' and 'content' already exists.")

    except Exception as e:
        logger.error(f"Failed to create text index: {e}")
        raise Exception("Could not create the text index.")


def normalize_vietnamese_text(query):
    """
    A more sophisticated normalization for Vietnamese text.
    Removes diacritics, lowercases, and handles stopwords.
    """
    normalized_query = normalize_text(query)  # Basic normalization (removing diacritics)
    
    # Tokenize the query and remove stopwords
    tokens = [word for word in normalized_query.split() if word not in STOPWORDS_VIETNAMESE]
    
    return ' '.join(tokens)


def retrieve_articles(query, page=1, limit=5, sort_by='score', order='desc', filters=None):
    """
    Retrieves articles from the MongoDB collection using full-text search and additional filters.
    Supports sorting by relevance (text score) or date and pagination.
    """
    collection = get_mongo_collection('newsdb', 'articles')
    try:
        # Normalize and clean the query for Vietnamese
        normalized_query = normalize_vietnamese_text(query)

        # Full-text search using $text
        search_conditions = {"$text": {"$search": normalized_query}}

        # Apply additional filters if provided (e.g., date range, source)
        if filters:
            if "from_date" in filters and "to_date" in filters:
                try:
                    from_date = datetime.strptime(filters["from_date"], "%Y-%m-%d")
                    to_date = datetime.strptime(filters["to_date"], "%Y-%m-%d")
                    search_conditions["date"] = {"$gte": from_date, "$lte": to_date}
                except ValueError:
                    logger.warning("Invalid date format in filters. Ignoring date filters.")
            if "source" in filters:
                search_conditions["source"] = {"$regex": filters["source"], "$options": "i"}

        skip = (page - 1) * limit
        sort_order = -1 if order == 'desc' else 1

        # Sort by score (relevance) or date
        sort_criteria = [("score", {"$meta": "textScore"})] if sort_by == 'score' else [("date", sort_order)]

        # Execute the search
        articles = list(
            collection.find(search_conditions, {"score": {"$meta": "textScore"}})
            .sort(sort_criteria)
            .skip(skip)
            .limit(limit)
        )

        return articles

    except PyMongoError as e:
        logger.error(f"Failed to retrieve articles: {e}")
        raise Exception(f"Failed to retrieve articles: {str(e)}")


def get_search_filters(from_date=None, to_date=None, source=None):
    """
    Helper to construct filters for search based on date range and source.
    """
    filters = {}
    if from_date and to_date:
        filters["from_date"] = from_date
        filters["to_date"] = to_date
    if source:
        filters["source"] = source
    return filters
