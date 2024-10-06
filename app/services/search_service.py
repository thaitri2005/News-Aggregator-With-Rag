#app/services/search_service.py
from pymongo.errors import PyMongoError
from utils.common import normalize_text, get_mongo_collection
import logging

logger = logging.getLogger(__name__)

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

def retrieve_articles(query, page=1, limit=5, sort_by='score', order='desc'):
    collection = get_mongo_collection('newsdb', 'articles')
    try:
        # Ensure the query is normalized
        normalized_query = normalize_text(query)

        # Use $text to search with MongoDB's full-text search capabilities
        search_conditions = {"$text": {"$search": normalized_query}}

        skip = (page - 1) * limit
        sort_order = -1 if order == 'desc' else 1

        # Execute the search with $meta textScore for relevance-based sorting
        articles = list(
            collection.find(search_conditions, {"score": {"$meta": "textScore"}})
            .sort([("score", {"$meta": "textScore"})])  # Sort by text score
            .skip(skip)
            .limit(limit)
        )

        return articles
    except PyMongoError as e:
        raise Exception(f"Failed to retrieve articles: {str(e)}")
