from pymongo import MongoClient
import os

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client.newsdb

    def get_collection(self, name):
        return self.db[name]

db = Database()


articles_collection = db.get_collection('articles')
summaries_collection = db.get_collection('summaries')
queries_collection = db.get_collection('queries')
