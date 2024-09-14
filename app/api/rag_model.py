# app/api/rag_model.py
import sys
import os
import logging
from bson import ObjectId

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db

logger = logging.getLogger(__name__)

def convert_objectid_to_str(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
    return doc

def create_text_index():
    """
    Creates a text index on the title and content fields of the articles collection.
    """
    try:
        articles_collection = db.get_collection('articles')
        articles_collection.create_index([("title", "text"), ("content", "text")])
        logger.info("Text index created on 'title' and 'content' fields.")
    except Exception as e:
        logger.exception("Failed to create text index.")

def retrieve_articles(query, page=1, limit=5):
    try:
        articles_collection = db.get_collection('articles')
        skip = (page - 1) * limit
        search_results = articles_collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)

        return [convert_objectid_to_str(result) for result in search_results]
    except Exception as e:
        logger.exception("Failed to retrieve articles.")
        return []

if __name__ == "__main__":
    create_text_index()
