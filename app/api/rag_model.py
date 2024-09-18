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

        # Create a weighted index, giving higher priority to 'title'
        if not index_exists:
            articles_collection.create_index(
                [("title", "text"), ("content", "text")],
                weights={"title": 10, "content": 5},  # Higher weight for title
                name="title_content_text_index",
                default_language="english"
            )
            logger.info("Text index with weighted priority on 'title' created successfully.")
        else:
            logger.info("Text index on 'title' and 'content' already exists.")

    except PyMongoError as e:
        logger.exception(f"Failed to create text index: {e}")

def retrieve_articles(query, page=1, limit=5, sort_by='score', order='desc', filters=None):
    try:
        articles_collection = db.get_collection('articles')

        # Validate and sanitize input
        sanitized_query = re.sub(r'[^\w\s]', '', query)

        # MongoDB text search with score
        mongo_query = {"$text": {"$search": sanitized_query}}

        # Define projection, include the score
        projection = {
            "score": {"$meta": "textScore"},
            "title": 1,
            "content": 1,
            "date": 1,
            "source_url": 1,
            "source": 1
        }

        # Sort by relevance (textScore) or other fields like 'date'
        sort_order = -1 if order == 'desc' else 1
        sort_field = 'score' if sort_by == 'score' else 'date'

        search_results = articles_collection.find(
            mongo_query,
            projection
        ).sort([(sort_field, {"$meta": "textScore"} if sort_field == 'score' else sort_order)]).skip((page - 1) * limit).limit(limit)

        articles = [convert_objectid_to_str(result) for result in search_results]
        return articles
    except PyMongoError as e:
        logger.exception(f"Failed to retrieve articles: {e}")
        return []

if __name__ == "__main__":
    create_text_index()
