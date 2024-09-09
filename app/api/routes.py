from flask import Blueprint, jsonify, request
from database import articles_collection, summaries_collection, queries_collection
from bson.objectid import ObjectId
from .gemini_integration import summarize_article
from .rag_model import retrieve_articles
import logging

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Helper function to convert ObjectId to string
def convert_objectid_to_str(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
    return doc

# Get all articles
@api.route('/articles', methods=['GET'])
def get_articles():
    articles = list(articles_collection.find({}, {"_id": 1, "title": 1, "content": 1, "date": 1, "source_url": 1}))
    articles = [convert_objectid_to_str(article) for article in articles]
    return jsonify(articles)

# Get a single article by ID
@api.route('/articles/<id>', methods=['GET'])
def get_article(id):
    try:
        article_id = ObjectId(id)
    except Exception as e:
        return jsonify({"error": f"Invalid article ID: {str(e)}"}), 400

    article = articles_collection.find_one({"_id": article_id})
    if article:
        article = convert_objectid_to_str(article)
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

# Summarize article
@api.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    article_text = data.get("article_text")    
    if not article_text:
        logger.error("No article text provided.")
        return jsonify({"error": "No article text provided"}), 400

    try:
        # Call the summarization function
        summary = summarize_article(article_text)
        logger.info(f"Generated summary: {summary}")
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logger.error(f"An error occurred during summarization: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Retrieve articles based on a search query
@api.route('/retrieve', methods=['POST'])
def retrieve():
    try:
        data = request.json
        query = data.get('query')
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 5))

        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        articles = retrieve_articles(query, page, limit)
        if not articles:
            return jsonify({"message": "No articles found"}), 404
        return jsonify(articles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
