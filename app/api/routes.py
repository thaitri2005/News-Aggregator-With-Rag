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
    date = fields.Str(required=True)  # Store date as a string for simplicity
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
    Adds a new article to Pinecone.
    """
    try:
        data = request.get_json()
        if not data:
            logger.error("No input data provided.")
            abort(400, description="No input data provided.")

        # Validate article schema
        article_schema = ArticleSchema()
        validated_data = article_schema.load(data)

        # Encode content and upsert the vector
        vector = vector_db.vectorizer.encode_text(validated_data["content"]).tolist()
        metadata = {
            "title": validated_data["title"],
            "chunk": validated_data["content"],  # Store under 'chunk'
            "source_url": validated_data["source_url"],
            "date": validated_data["date"],
            "source": validated_data["source"],
        }

        vector_db.upsert_vectors(
            vectors=[
                {"id": validated_data["source_url"], "values": vector, "metadata": metadata}
            ]
        )

        logger.info(f"Article '{validated_data['title']}' added successfully to Pinecone.")
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

        # Query Pinecone
        pinecone_results = vector_db.query_vectors(query, top_k=limit)

        # Prepare articles with metadata
        articles = []
        for result in pinecone_results:
            metadata = result["metadata"]
            if not metadata.get("chunk"):  # Use 'chunk' instead of 'content'
                logger.warning(f"Metadata for ID {result['id']} is missing 'chunk'. Skipping.")
                continue

            articles.append({
                "id": result["id"],
                "title": metadata.get("title", "Untitled"),
                "content": metadata.get("chunk", ""),  # Retrieve 'chunk'
                "source_url": metadata.get("source_url", ""),
                "date": metadata.get("date", ""),
                "source": metadata.get("source", "Unknown"),
                "relevance_score": result["score"],
            })

        # Sort articles
        if sort_by == "date":
            articles.sort(key=lambda x: x["date"], reverse=(order == "desc"))
        elif sort_by == "score":
            articles.sort(key=lambda x: x["relevance_score"], reverse=(order == "desc"))

        # Pagination
        start_index = (page - 1) * limit
        paginated_articles = articles[start_index : start_index + limit]

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
        # Log the incoming request
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
        results = vector_db.query_by_id(article_id)
        if not results:
            logger.error(f"Article not found with ID: {article_id}")
            abort(404, description="Article not found.")

        # Extract the content from the metadata
        metadata = next(iter(results))["metadata"]
        logger.debug(f"Retrieved metadata for article ID {article_id}: {metadata}")

        # Fetch and validate article content
        article_content = metadata.get("chunk", "")  # Use 'chunk' instead of 'content'
        if not article_content:
            logger.error(f"Content (chunk) is missing for article with ID: {article_id}")
            abort(404, description="Article content not found.")

        # Log the content and its length
        logger.debug(f"Article content length: {len(article_content)}")
        logger.debug(f"Article content (first 200 chars): {article_content[:200]}")

        # Summarize the article using Gemini API
        logger.info(f"Summarizing article with ID: {article_id}...")
        summary = summarize_article(article_content)
        
        if "error" in summary.lower():
            logger.error(f"Failed to summarize article with ID: {article_id}. Response: {summary}")
            return jsonify({"error": summary}), 500

        # Log the generated summary
        logger.info(f"Generated summary for article ID {article_id}: {summary}")
        return jsonify({"summary": summary}), 200

    except Exception as e:
        logger.exception("An error occurred during summarization.")
        abort(500, description="Internal server error.")

