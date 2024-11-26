#app/services/vector_db_service.py
from pinecone import Pinecone
from services.vectorizer_service import PhoBERTVectorizer
import os
import logging
import re

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        host = os.getenv("PINECONE_HOST")

        if not api_key or not host:
            raise ValueError("PINECONE_API_KEY and PINECONE_HOST must be set in the environment variables.")

        self.pinecone = Pinecone(api_key=api_key)
        self.index = self.pinecone.Index('aggregator', host=host)

        # Initialize PhoBERT for encoding
        self.vectorizer = PhoBERTVectorizer()

    def clean_text(self, text):
        """
        Cleans the input text by removing Vietnamese stop words, symbols, and excess spaces.
        """
        if not text:
            return ""

        # List of Vietnamese stop/linking words to remove
        stop_words = {"và", "nhưng", "hoặc", "cũng", "để", "đến", "là", "của", "có", "khi", "vì", "do", "nếu", "bởi", "đã"}

        # Remove special characters, extra spaces, and stop words
        text = re.sub(r"[^\w\s]", " ", text)  # Remove special characters
        text = re.sub(r"\s+", " ", text).strip()  # Remove excess spaces
        words = text.split()
        cleaned_words = [word for word in words if word.lower() not in stop_words]
        cleaned_text = " ".join(cleaned_words)

        logger.debug(f"Cleaned text: {cleaned_text[:200]}...")  # Log a sample of the cleaned text
        return cleaned_text

    def upsert_vectors(self, vectors, namespace="default"):
        """
        Upserts a batch of vectors to Pinecone.
        """
        if not vectors:
            logger.warning("No vectors to upsert.")
            return
        try:
            logger.info(f"Upserting {len(vectors)} vectors to namespace '{namespace}'...")
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info("Upsert successful.")
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            raise

    def query_vectors(self, query, namespace="default", top_k=5):
        """
        Queries the Pinecone index for top-k similar vectors.
        """
        query = self.clean_text(query)  # Clean the query text
        query_vector = self.vectorizer.encode_text(query).tolist()

        try:
            logger.info(f"Querying Pinecone with cleaned query: '{query[:200]}...'")
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
            )
            matches = [
                {"id": match["id"], "score": match["score"], "metadata": match["metadata"]}
                for match in response["matches"]
            ]
            logger.info(f"Found {len(matches)} matches.")
            return matches
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def query_by_id(self, article_id, namespace="default"):
        """
        Fetches metadata for a specific article ID.
        """
        try:
            results = self.index.fetch(ids=[article_id], namespace=namespace)
            if "vectors" not in results or not results["vectors"]:
                logger.warning(f"No results found for ID: {article_id}")
                return []
            return results["vectors"].values()
        except Exception as e:
            logger.error(f"Error fetching vector by ID: {e}")
            raise

    def delete_all(self, namespace="default"):
        """
        Deletes all vectors in a given namespace using the Pinecone `delete` method.
        """
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Successfully deleted all vectors in namespace '{namespace}'.")
        except Exception as e:
            logger.error(f"Failed to delete all vectors in namespace '{namespace}': {e}")
            raise
