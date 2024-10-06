#app/utils/common.py
import os
from bson import ObjectId
from pymongo import MongoClient
import logging
import unicodedata
import re

logger = logging.getLogger(__name__)

def load_mongo_uri():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in environment variables.")
    return mongo_uri

def get_mongo_collection(db_name, collection_name):
    try:
        client = MongoClient(load_mongo_uri())
        db = client[db_name]
        return db[collection_name]
    except Exception as e:
        logger.exception(f"Failed to get collection '{collection_name}': {str(e)}")
        raise ConnectionError("Failed to connect to MongoDB.")

def normalize_text(text):
    """
    Normalize Vietnamese text by removing diacritics, converting to lowercase, 
    and removing unnecessary punctuation. This improves search accuracy.
    """
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    sanitized_text = re.sub(r'[^\w\s]', '', normalized_text)
    return sanitized_text.strip()

def convert_objectid_to_str(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, (dict, list)):
                doc[key] = convert_objectid_to_str(value)
    elif isinstance(doc, list):
        doc = [convert_objectid_to_str(item) for item in doc]
    return doc
