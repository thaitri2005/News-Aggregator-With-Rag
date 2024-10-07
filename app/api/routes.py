from flask import Blueprint, jsonify, request, abort
from database import articles_collection
from bson.objectid import ObjectId
from .gemini_integration import summarize_article
from marshmallow import Schema, fields, ValidationError
from services.search_service import retrieve_articles, get_search_filters  # Updated import
import logging

from utils.common import convert_objectid_to_str 

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
    from_date = fields.Date(required=False)  # Optional filter
    to_date = fields.Date(required=False)    # Optional filter
    source = fields.Str(required=False)      # Optional filter

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

# Summarize article
@api.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        article_id = data.get("article_id")

        if not article_id:
            logger.error("No article ID provided.")
            abort(400, description="No article ID provided.")

        # Fetch the article by its ID
        article = articles_collection.find_one({"_id": ObjectId(article_id)})

        if not article:
            logger.error(f"Article not found with ID: {article_id}")
            abort(404, description="Article not found.")

        # Check if the summary already exists
        if "summary" in article and article["summary"]:
            logger.info(f"Returning existing summary for article {article_id}.")
            return jsonify({"summary": article["summary"]}), 200

        # If no summary exists, generate a new one
        article_text = article.get("content")
        summary = summarize_article(article_text)

        # Handle errors
        if "error" in summary.lower():
            logger.error(f"Failed to summarize article {article_id}.")
            return jsonify({"error": summary}), 500

        # Update the article with the new summary
        articles_collection.update_one({"_id": ObjectId(article_id)}, {"$set": {"summary": summary}})
        return jsonify({"summary": summary}), 200

    except Exception as e:
        logger.exception("An error occurred during summarization.")
        abort(500, description="Internal server error.")

# Retrieve articles based on a search query
@api.route('/retrieve', methods=['POST'])
def retrieve():
    try:
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        retrieve_schema = RetrieveSchema()
        validated_data = retrieve_schema.load(data)

        query = validated_data.get('query').strip()
        page = validated_data.get('page')
        limit = validated_data.get('limit')
        sort_by = validated_data.get('sort_by')
        order = validated_data.get('order')

        # Optional filters
        from_date = validated_data.get('from_date')
        to_date = validated_data.get('to_date')
        source = validated_data.get('source')

        # Pass filters to the search service
        filters = get_search_filters(from_date, to_date, source)

        # Retrieve articles using the improved search service
        articles = retrieve_articles(query, page, limit, sort_by, order, filters)

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
