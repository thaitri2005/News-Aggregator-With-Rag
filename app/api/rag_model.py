import os
import logging
from pymongo import TEXT
from pymongo.errors import PyMongoError
import re

from bson import ObjectId
from utils import convert_objectid_to_str
from database import db

logger = logging.getLogger(__name__)

def create_text_index():
    """
    Ensures that a text index on the 'title' and 'content' fields of the articles collection exists, 
    with even higher priority given to the 'title'.
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

        # Create a weighted index, giving a significantly higher weight to 'title'
        if not index_exists:
            articles_collection.create_index(
                [("title", "text"), ("content", "text")],
                weights={"title": 20, "content": 5},  # Even higher weight for title
                name="title_content_text_index",
                default_language="vietnamese"  # Use Vietnamese as the default language
            )
            logger.info("Text index with even higher priority on 'title' created successfully.")
        else:
            logger.info("Text index on 'title' and 'content' already exists.")

    except PyMongoError as e:
        logger.exception(f"Failed to create text index: {e}")

def retrieve_articles(query, page=1, limit=5, sort_by='score', order='desc', filters=None):
    try:
        articles_collection = db.get_collection('articles')

        # Sanitize and prioritize the query
        sanitized_query = re.sub(r'[^\w\s]', '', query)

        # MongoDB full-text search with weighted priority on title
        text_search_query = {"$text": {"$search": sanitized_query}}

        # Separate regex-based search for the title (for exact or partial matches in the title)
        title_regex_query = {"title": {"$regex": sanitized_query, "$options": "i"}}

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

        # Execute full-text search (search both title and content, with title weighted higher)
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

        # Combine title-based and content-based results, prioritizing title matches
        combined_results = list(title_search_results) + list(text_search_results)

        # Ensure results contain the actual query (keyword-based filtering)
        filtered_results = [
            article for article in combined_results
            if sanitized_query.lower() in article.get('title', '').lower() or sanitized_query.lower() in article.get('content', '').lower()
        ]

        # Remove duplicates by ObjectId and prioritize title-based matches
        unique_results = {str(result['_id']): result for result in filtered_results}

        # Ensure pagination is applied
        articles = list(unique_results.values())[:limit]

        return articles
    except PyMongoError as e:
        logger.exception(f"Failed to retrieve articles: {e}")
        return []

if __name__ == "__main__":
    create_text_index()
