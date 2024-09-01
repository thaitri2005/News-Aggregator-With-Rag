from flask import Blueprint, jsonify, request
from database import articles_collection, summaries_collection, queries_collection
from bson.objectid import ObjectId

api = Blueprint('api', __name__)

# Get all articles
@api.route('/articles', methods=['GET'])
def get_articles():
    articles = list(articles_collection.find({}, {"_id": 0}))  # Exclude the MongoDB _id field
    return jsonify(articles)

# Get a single article by ID
@api.route('/articles/<id>', methods=['GET'])
def get_article(id):
    article = articles_collection.find_one({"_id": ObjectId(id)}, {"_id": 0})
    if article:
        return jsonify(article)
    else:
        return jsonify({"error": "Article not found"}), 404

# Add a new article
@api.route('/articles', methods=['POST'])
def add_article():
    data = request.json
    articles_collection.insert_one({
        "title": data["title"],
        "content": data["content"],
        "date": data["date"],
        "source_url": data["source_url"]
    })
    return jsonify({"message": "Article added successfully"}), 201

# Get summaries
# Helper function to convert ObjectId to string
def convert_objectid_to_str(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
    return doc

@api.route('/summaries', methods=['GET'])
def get_summaries():
    summaries = list(summaries_collection.find())
    summaries = [convert_objectid_to_str(summary) for summary in summaries]
    return jsonify(summaries)

# Get queries
@api.route('/queries', methods=['GET'])
def get_queries():
    queries = list(queries_collection.find({}, {"_id": 0}))
    return jsonify(queries)

# Add a new query
@api.route('/queries', methods=['POST'])
def add_query():
    data = request.json
    queries_collection.insert_one({
        "query": data["query"],
        "response": data["response"]
    })
    return jsonify({"message": "Query added successfully"}), 201
