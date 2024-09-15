# app/api/routes.py

from flask import Blueprint, jsonify, request, abort
from database import articles_collection, summaries_collection, queries_collection
from bson.objectid import ObjectId
from .gemini_integration import summarize_article
from .rag_model import retrieve_articles
import logging

from utils import convert_objectid_to_str  # Import from utils.py
from marshmallow import Schema, fields, ValidationError

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Schemas for input validation using marshmallow
class ArticleSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    date = fields.DateTime(required=True)
    source_url = fields.Url(required=True)

class QuerySchema(Schema):
    query = fields.Str(required=True)
    response = fields.Str(required=True)

class RetrieveSchema(Schema):
    query = fields.Str(required=True)
    page = fields.Int(missing=1, validate=lambda n: n > 0)
    limit = fields.Int(missing=5, validate=lambda n: n > 0)
    sort_by = fields.Str(missing='score', validate=lambda x: x in ['score', 'date'])
    order = fields.Str(missing='desc', validate=lambda x: x in ['asc', 'desc'])

# Get all articles
@api.route('/articles', methods=['GET'])
def get_articles():
    try:
        articles = list(articles_collection.find({}, {
            "_id": 1, "title": 1, "content": 1, "date": 1, "source_url": 1, "source": 1
        }))
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
        article = articles_collection.find_one({"_id": article_id})
        if article:
            article = convert_objectid_to_str(article)
            return jsonify(article), 200
        else:
            logger.warning(f"Article not found for ID: {id}")
            abort(404, description="Article not found.")
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid article ID: {str(e)}")
        abort(400, description="Invalid article ID.")
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        abort(500, description="Internal server error.")

# Add a new article
@api.route('/articles', methods=['POST'])
def add_article():
    try:
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        article_schema = ArticleSchema()
        validated_data = article_schema.load(data)
        articles_collection.insert_one(validated_data)
        logger.info("Article added successfully.")
        return jsonify({"message": "Article added successfully"}), 201
    except ValidationError as ve:
        logger.error(f"Validation error: {ve.messages}")
        abort(400, description=ve.messages)
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
    try:
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        query_schema = QuerySchema()
        validated_data = query_schema.load(data)
        queries_collection.insert_one(validated_data)
        logger.info("Query added successfully.")
        return jsonify({"message": "Query added successfully"}), 201
    except ValidationError as ve:
        logger.error(f"Validation error: {ve.messages}")
        abort(400, description=ve.messages)
    except Exception as e:
        logger.exception("Failed to add new query.")
        abort(500, description="Internal server error.")

# Summarize article
@api.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        article_text = data.get("article_text")
        if not article_text:
            logger.error("No article text provided.")
            abort(400, description="No article text provided.")

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
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        # Validate input data using marshmallow schema
        retrieve_schema = RetrieveSchema()
        validated_data = retrieve_schema.load(data)

        query = validated_data.get('query')
        page = validated_data.get('page')
        limit = validated_data.get('limit')
        sort_by = 'date'  # Sort by date to get latest articles
        order = validated_data.get('order')

        # Determine the sorting order for MongoDB
        sort_order = -1 if order == 'desc' else 1  # Default to descending for latest first

        # MongoDB allows for text search using $text index for full-text search
        skip = (page - 1) * limit

        # Perform the search in MongoDB using text search and pagination
        articles = list(articles_collection.find(
            {"$text": {"$search": query}}  # Full-text search on the article content
        ).sort([(sort_by, sort_order)])  # Sort by date descending to get latest articles first
        .skip(skip).limit(limit))

        # If articles are found, convert ObjectId to strings
        if articles:
            articles = [convert_objectid_to_str(article) for article in articles]
            return jsonify(articles), 200
        else:
            logger.info("No articles found matching the query.")
            return jsonify({"message": "No articles found"}), 404
    except ValidationError as ve:
        logger.error(f"Validation error: {ve.messages}")
        abort(400, description=ve.messages)
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
