# app/api/routes.py
from flask import Blueprint, jsonify, request, abort
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
    try:
        articles = list(articles_collection.find({}, {"_id": 1, "title": 1, "content": 1, "date": 1, "source_url": 1}))
        articles = [convert_objectid_to_str(article) for article in articles]
        return jsonify(articles), 200
    except Exception as e:
        logger.exception("Failed to fetch articles.")
        abort(500, description="Internal server error.")

# Get a single article by ID
@api.route('/articles/<id>', methods=['GET'])
def get_article(id):
    try:
        article_id = ObjectId(id)
    except Exception as e:
        logger.error(f"Invalid article ID: {str(e)}")
        abort(400, description="Invalid article ID.")

    article = articles_collection.find_one({"_id": article_id})
    if article:
        article = convert_objectid_to_str(article)
        return jsonify(article), 200
    else:
        logger.warning(f"Article not found for ID: {id}")
        abort(404, description="Article not found.")

# Add a new article
@api.route('/articles', methods=['POST'])
def add_article():
    data = request.json
    try:
        articles_collection.insert_one({
            "title": data["title"],
            "content": data["content"],
            "date": data["date"],
            "source_url": data["source_url"]
        })
        logger.info("Article added successfully.")
        return jsonify({"message": "Article added successfully"}), 201
    except Exception as e:
        logger.exception("Failed to add new article.")
        abort(500, description="Internal server error.")

# Get summaries
@api.route('/summaries', methods=['GET'])
def get_summaries():
    try:
        summaries = list(summaries_collection.find())
        summaries = [convert_objectid_to_str(summary) for summary in summaries]
        return jsonify(summaries), 200
    except Exception as e:
        logger.exception("Failed to fetch summaries.")
        abort(500, description="Internal server error.")

# Get queries
@api.route('/queries', methods=['GET'])
def get_queries():
    try:
        queries = list(queries_collection.find({}, {"_id": 0}))
        return jsonify(queries), 200
    except Exception as e:
        logger.exception("Failed to fetch queries.")
        abort(500, description="Internal server error.")

# Add a new query
@api.route('/queries', methods=['POST'])
def add_query():
    data = request.json
    try:
        queries_collection.insert_one({
            "query": data["query"],
            "response": data["response"]
        })
        logger.info("Query added successfully.")
        return jsonify({"message": "Query added successfully"}), 201
    except Exception as e:
        logger.exception("Failed to add new query.")
        abort(500, description="Internal server error.")

# Summarize article
@api.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    article_text = data.get("article_text")
    if not article_text:
        logger.error("No article text provided.")
        abort(400, description="No article text provided.")

    try:
        # Call the summarization function
        summary = summarize_article(article_text)
        logger.info("Article summarized successfully.")
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logger.exception("An error occurred during summarization.")
        abort(500, description="An error occurred while processing the article summary.")

# Retrieve articles based on a search query
@api.route('/retrieve', methods=['POST'])
def retrieve():
    try:
        data = request.json
        query = data.get('query')
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 5))

        if not query:
            logger.error("Query parameter is required.")
            abort(400, description="Query parameter is required.")

        articles = retrieve_articles(query, page, limit)
        if not articles:
            logger.info("No articles found matching the query.")
            return jsonify({"message": "No articles found"}), 404
        return jsonify(articles), 200
    except Exception as e:
        logger.exception("An error occurred during article retrieval.")
        abort(500, description="Internal server error.")

# Error handler for 400 Bad Request
@api.errorhandler(400)
def bad_request(error):
    response = jsonify({"error": str(error.description)})
    response.status_code = 400
    return response

# Error handler for 404 Not Found
@api.errorhandler(404)
def not_found(error):
    response = jsonify({"error": str(error.description)})
    response.status_code = 404
    return response

# Error handler for 500 Internal Server Error
@api.errorhandler(500)
def internal_error(error):
    response = jsonify({"error": str(error.description)})
    response.status_code = 500
    return response
