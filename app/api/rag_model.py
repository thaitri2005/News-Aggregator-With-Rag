# app/api/rag_model.py

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
    Ensures that a text index on the 'title' and 'content' fields of the articles collection exists.
    """
    try:
        # Get the articles collection
        articles_collection = db.get_collection('articles')

        # Get existing indexes
        existing_indexes = articles_collection.index_information()

        # Define the desired index fields (title and content, not summary)
        desired_fields = {'title', 'content'}
        index_exists = False
        conflicting_index = None

        # Check if an index with the same fields exists
        for index_name, index_info in existing_indexes.items():
            if index_info.get('weights'):
                index_fields = set(index_info['weights'].keys())
                if index_fields == desired_fields:
                    if index_name == 'title_content_text_index':
                        index_exists = True
                    else:
                        conflicting_index = index_name
                    break

        # Drop the conflicting index if it exists
        if conflicting_index and not index_exists:
            logger.info(f"Dropping conflicting index: {conflicting_index}")
            articles_collection.drop_index(conflicting_index)

        # Create the new index if it doesn't exist
        if not index_exists:
            articles_collection.create_index(
                [("title", TEXT), ("content", TEXT)],
                name='title_content_text_index',
                default_language='english'
            )
            logger.info("Text index created on 'title' and 'content' fields.")
        else:
            logger.info("Text index on 'title' and 'content' already exists.")

    except PyMongoError as e:
        logger.exception(f"Failed to create text index: {e}")

def retrieve_articles(query, page=1, limit=5, sort_by='score', order='desc', filters=None):
    """
    Retrieves articles based on the search query and optional filters.

    Parameters:
        query (str): The search query string.
        page (int): The page number for pagination.
        limit (int): The number of articles per page.
        sort_by (str): The field to sort by ('score', 'date').
        order (str): Sort order ('asc' or 'desc').
        filters (dict): Additional filters (e.g., date range, source).

    Returns:
        list: A list of articles matching the search criteria.
    """
    try:
        articles_collection = db.get_collection('articles')

        # Validate and sanitize input parameters
        if not isinstance(query, str) or not query.strip():
            logger.error("Invalid query parameter.")
            return []

        try:
            page = int(page)
            limit = int(limit)
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            logger.error("Page and limit must be positive integers.")
            return []

        skip = (page - 1) * limit

        # Sanitize the query to prevent injection attacks
        sanitized_query = re.sub(r'[^\w\s]', '', query)

        # Build the MongoDB query
        mongo_query = {"$text": {"$search": sanitized_query}}

        # Apply additional filters if provided
        if filters:
            mongo_query.update(filters)

        # Define the projection
        projection = {
            "score": {"$meta": "textScore"},
            "title": 1,
            "content": 1,
            "date": 1,
            "source_url": 1,
            "source": 1
        }

        # Define the sort order
        if sort_by == 'date':
            sort_field = 'date'
        else:
            sort_field = 'score'

        sort_order = -1 if order == 'desc' else 1

        # Execute the query
        search_results = articles_collection.find(
            mongo_query,
            projection
        ).sort([(sort_field, {"$meta": "textScore"} if sort_field == 'score' else sort_order)]).skip(skip).limit(limit)

        articles = []
        for result in search_results:
            article = convert_objectid_to_str(result)
            articles.append(article)

        return articles

    except PyMongoError as e:
        logger.exception(f"Failed to retrieve articles: {e}")
        return []
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return []

if __name__ == "__main__":
    create_text_index()
