#app/api/rag_model.py
import os
import logging
from pymongo import TEXT
from pymongo.errors import PyMongoError
import re
import unicodedata

from bson import ObjectId
from utils import convert_objectid_to_str
from database import db

logger = logging.getLogger(__name__)

def normalize_text(text):
    """
    Normalize Vietnamese text by removing diacritics, converting to lowercase, 
    and removing unnecessary punctuation. This improves search accuracy.
    """
    # Normalize diacritics and convert to lowercase
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    # Remove any non-word characters
    sanitized_text = re.sub(r'[^\w\s]', '', normalized_text)
    return sanitized_text.strip()

def create_text_index():
    """
    Ensures that a text index on the 'title' and 'content' fields of the articles collection exists,
    with higher priority given to the 'title'.
    """
    try:
        articles_collection = db.get_collection('articles')

        # Get existing indexes
        existing_indexes = articles_collection.index_information()

        # Check if the desired index exists
        index_exists = False
        conflicting_index = None
        desired_fields = {'title', 'content'}

        for index_name, index_info in existing_indexes.items():
            if index_info.get('weights'):
                index_fields = set(index_info['weights'].keys())
                if index_fields == desired_fields:
                    if index_name == 'title_content_text_index':
                        index_exists = True
                    else:
                        conflicting_index = index_name
                    break

        if conflicting_index and not index_exists:
            articles_collection.drop_index(conflicting_index)

        # Create a weighted index, giving a higher weight to 'title'
        if not index_exists:
            articles_collection.create_index(
                [("title", "text"), ("content", "text")],
                weights={"title": 20, "content": 5},  # Higher weight for 'title'
                name="title_content_text_index",
                default_language="none"  # For better control, avoid using Mongo's language analyzer
            )
            logger.info("Text index with priority on 'title' created successfully.")
        else:
            logger.info("Text index on 'title' and 'content' already exists.")

    except PyMongoError as e:
        logger.exception(f"Failed to create text index: {e}")

def retrieve_articles(query, page=1, limit=5, sort_by='score', order='desc', filters=None):
    """
    Retrieves articles from the MongoDB collection using both regex-based and full-text search.
    The title is prioritized with higher ranking, and pagination and sorting are applied.
    """
    try:
        articles_collection = db.get_collection('articles')

        # Normalize and prioritize the query for Vietnamese text
        normalized_query = normalize_text(query)

        # MongoDB full-text search with weighted priority on title and content
        text_search_query = {"$text": {"$search": normalized_query}}

        # Separate regex-based search for title (for exact or partial matches)
        title_regex_query = {"title": {"$regex": normalized_query, "$options": "i"}}

        # Execute title search first (prioritize title matches)
        title_search_results = articles_collection.find(
            title_regex_query,
            {
                "score": {"$meta": "textScore"},
                "title": 1,
                "content": 1,
                "date": 1,
                "source_url": 1,
                "source": 1
            }
        ).sort([("date", -1)]).skip((page - 1) * limit).limit(limit)

        # Execute full-text search (search both title and content)
        text_search_results = articles_collection.find(
            text_search_query,
            {
                "score": {"$meta": "textScore"},
                "title": 1,
                "content": 1,
                "date": 1,
                "source_url": 1,
                "source": 1
            }
        ).sort([("score", {"$meta": "textScore"} if sort_by == 'score' else -1)]).skip((page - 1) * limit).limit(limit)

        # Combine title-based and content-based results, prioritize title matches
        combined_results = list(title_search_results) + list(text_search_results)

        # Ensure results contain the actual query (keyword-based filtering)
        filtered_results = [
            article for article in combined_results
            if normalized_query in normalize_text(article.get('title', '')) or
               normalized_query in normalize_text(article.get('content', ''))
        ]

        # Remove duplicates by ObjectId, prioritize title-based matches
        unique_results = {str(result['_id']): result for result in filtered_results}

        # Pagination: Apply page size and limit to the final results
        paginated_results = list(unique_results.values())[:limit]

        return paginated_results

    except PyMongoError as e:
        logger.exception(f"Failed to retrieve articles: {e}")
        return []

if __name__ == "__main__":
    create_text_index()
