# app/api/routes.py
from flask import Blueprint, jsonify, request, abort
from marshmallow import Schema, fields, ValidationError
from services.vector_db_service import VectorDBService
from .gemini_integration import summarize_article
import logging

api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)
vector_db = VectorDBService()

# Schemas for input validation
class ArticleSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    date = fields.Str(required=True)  # Store date as a string in ISO 8601 format
    source_url = fields.Url(required=True)
    source = fields.Str(required=True)

class RetrieveSchema(Schema):
    query = fields.Str(required=True)
    page = fields.Int(missing=1, validate=lambda n: n > 0)
    limit = fields.Int(missing=5, validate=lambda n: n > 0)
    sort_by = fields.Str(missing="score", validate=lambda x: x in ["score", "date"])
    order = fields.Str(missing="desc", validate=lambda x: x in ["asc", "desc"])


@api.route("/articles", methods=["POST"])
def add_article():
    """
    Adds a new article to Pinecone, vectorizing only the title and storing the content as metadata.
    """
    try:
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        # Validate article schema
        article_schema = ArticleSchema()
        validated_data = article_schema.load(data)

        # Vectorize the title
        title_vector = vector_db.vectorizer.encode_text(validated_data["title"])
        if title_vector is None:
            logger.error("Failed to vectorize the title.")
            abort(400, description="Failed to vectorize the title.")

        # Prepare metadata
        metadata = {
            "title": validated_data["title"],
            "content": validated_data["content"],
            "source_url": validated_data["source_url"],
            "date": validated_data["date"],
            "source": validated_data["source"],
        }

        # Create vector data for the title
        vector = {
            "id": f"{validated_data['source_url']}-title",
            "values": title_vector.tolist(),
            "metadata": metadata,
        }

        # Upsert the title vector
        vector_db.upsert_vectors([vector], namespace="title")
        logger.info(f"Article '{validated_data['title']}' added successfully.")
        return jsonify({"message": "Article added successfully"}), 201

    except ValidationError as ve:
        logger.error(f"Validation error: {ve.messages}")
        abort(400, description=ve.messages)
    except Exception as e:
        logger.exception("Failed to add new article.")
        abort(500, description="Internal server error.")


@api.route("/retrieve", methods=["POST"])
def retrieve():
    """
    Retrieves articles based on a query and ranks them using Pinecone.
    """
    try:
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        # Validate retrieve schema
        retrieve_schema = RetrieveSchema()
        validated_data = retrieve_schema.load(data)

        query = validated_data["query"].strip()
        if not query:
            logger.error("Empty query provided.")
            abort(400, description="Query cannot be empty.")

        page = validated_data["page"]
        limit = validated_data["limit"]
        sort_by = validated_data["sort_by"]
        order = validated_data["order"]

        # Query only the title vectors
        results = vector_db.query_vectors(query, namespace="title", top_k=limit * 2)

        if not results:
            logger.info(f"No results found for query '{query}'.")
            return jsonify([]), 200

        # Prepare articles with metadata
        articles = [
            {
                "id": result["id"],
                "title": result["metadata"].get("title", "Untitled"),
                "content": result["metadata"].get("content", ""),
                "source_url": result["metadata"].get("source_url", ""),
                "date": result["metadata"].get("date", ""),
                "source": result["metadata"].get("source", "Unknown"),
                "relevance_score": result["score"],
            }
            for result in results
        ]

        # Sort articles
        if sort_by == "date":
            articles.sort(key=lambda x: x["date"], reverse=(order == "desc"))
        elif sort_by == "score":
            articles.sort(key=lambda x: x["relevance_score"], reverse=(order == "desc"))

        # Pagination
        start_index = (page - 1) * limit
        paginated_articles = articles[start_index: start_index + limit]

        logger.info(f"Retrieved {len(paginated_articles)} articles for query '{query}'.")
        return jsonify(paginated_articles), 200

    except ValidationError as ve:
        logger.error(f"Validation error: {ve.messages}")
        abort(400, description=ve.messages)
    except Exception as e:
        logger.exception("An error occurred during article retrieval.")
        abort(500, description="Internal server error.")


@api.route("/clear", methods=["DELETE"])
def clear_database():
    """
    Deletes all vectors in the specified namespace or the default namespace.
    """
    try:
        namespace = request.args.get("namespace", "default").strip()
        if not namespace:
            logger.error("Invalid namespace provided.")
            abort(400, description="Namespace cannot be empty.")

        vector_db.delete_all(namespace=namespace)
        logger.info(f"All vectors in namespace '{namespace}' have been deleted.")
        return jsonify({"message": f"All vectors in namespace '{namespace}' have been deleted."}), 200
    except Exception as e:
        logger.error("Failed to clear the Pinecone database.")
        abort(500, description="Failed to clear the Pinecone database.")


@api.route("/summarize", methods=["POST"])
def summarize():
    """
    Summarizes an article using the Gemini API.
    """
    try:
        data = request.get_json()
        logger.debug(f"Received summarize request payload: {data}")

        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        article_id = data.get("article_id")
        if not article_id:
            logger.error("No article ID provided in the request.")
            abort(400, description="No article ID provided.")

        # Fetch metadata for the article by its ID
        logger.debug(f"Querying vector DB for article ID: {article_id}")
        results = vector_db.query_by_id(article_id, namespace="title")
        if not results:
            logger.error(f"Article not found with ID: {article_id}")
            abort(404, description="Article not found.")

        metadata = next(iter(results))["metadata"]
        article_content = metadata.get("content", "")
        if not article_content:
            logger.error(f"Content is missing for article with ID: {article_id}")
            abort(404, description="Article content not found.")

        # Summarize the article
        logger.info(f"Summarizing article with ID: {article_id}...")
        summary = summarize_article(article_content)

        if "error" in summary.lower():
            logger.error(f"Failed to summarize article with ID: {article_id}. Response: {summary}")
            return jsonify({"error": summary}), 500

        logger.info(f"Generated summary for article ID {article_id}: {summary}")
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logger.exception("An error occurred during summarization.")
        abort(500, description="Internal server error.")
