import sys
import os
from bson import ObjectId
# Adjust the path to make sure the correct reference is made
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db  # This will correctly import from the parent directory

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
    articles_collection = db.get_collection('articles')
    articles_collection.create_index([("title", "text"), ("content", "text")])

def retrieve_articles(query, page=1, limit=5):
    articles_collection = db.get_collection('articles')
    skip = (page - 1) * limit
    search_results = articles_collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)

    return [convert_objectid_to_str(result) for result in search_results]


if __name__ == "__main__":
    create_text_index()
