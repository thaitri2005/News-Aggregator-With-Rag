from pymongo import MongoClient, errors
import os

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(os.getenv("MONGO_URI"))
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