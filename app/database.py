from pymongo import MongoClient, errors
import os

class Database:
    def __init__(self):
        try:
            mongo_uri = os.getenv("MONGO_URI")  # Get MONGO_URI from environment
            self.client = MongoClient(mongo_uri, maxPoolSize=100, minPoolSize=10)
            self.db = self.client.newsdb
            print("Database connection established.")
        except errors.ServerSelectionTimeoutError as err:
            print(f"Database connection failed: {err}")
            self.db = None

    def get_collection(self, name):
        if self.db is not None:
            return self.db[name]
        else:
            raise ConnectionError("Failed to connect to the database.")

db = Database()

articles_collection = db.get_collection('articles')
summaries_collection = db.get_collection('summaries')
queries_collection = db.get_collection('queries')
