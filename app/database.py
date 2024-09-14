# app/database.py
import os
import logging
from pymongo import MongoClient, errors

# Set up logging
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI is not set in environment variables.")
            
            self.client = MongoClient(mongo_uri, maxPoolSize=100, minPoolSize=10)
            # Trigger a server selection to validate the connection
            self.client.admin.command('ping')
            self.db = self.client.newsdb
            logger.info("Database connection established.")
        except ValueError as ve:
            logger.error(f"Environment variable error: {ve}")
            self.db = None
        except errors.ServerSelectionTimeoutError as err:
            logger.error(f"Database connection failed: {err}")
            self.db = None
        except Exception as e:
            logger.exception("An unexpected error occurred during database initialization.")
            self.db = None

    def get_collection(self, name):
        if self.db is not None:
            try:
                return self.db[name]
            except Exception as e:
                logger.exception(f"Failed to get collection '{name}'.")
                raise
        else:
            logger.error("Attempted to get a collection without a database connection.")
            raise ConnectionError("Failed to connect to the database.")

# Initialize the Database instance
db = Database()

# Get collections
try:
    articles_collection = db.get_collection('articles')
    summaries_collection = db.get_collection('summaries')
    queries_collection = db.get_collection('queries')
except Exception as e:
    logger.error("Failed to initialize collections.")
