#app/services/vector_db_service.py
from pinecone import Pinecone
from services.vectorizer_service import PhoBERTVectorizer
import os
import logging

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

    def upsert_vectors(self, vectors, namespace="default"):
        """
        Upserts a batch of vectors to Pinecone.
        """
        if not vectors:
            raise ValueError("No vectors to upsert.")
        try:
            logger.info(f"Upserting {len(vectors)} vectors to namespace '{namespace}'...")
            logger.debug(f"Vectors: {vectors}")
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info("Upsert successful.")
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            raise


    def query_vectors(self, query, namespace="default", top_k=5):
        """
        Queries the Pinecone index for top-k similar vectors.
        """
        query_vector = self.vectorizer.encode_text(query).tolist()
        try:
            logger.info(f"Querying Pinecone with vector for query '{query}'...")
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
            )
            logger.debug(f"Query response: {response}")
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
        results = self.index.fetch(ids=[article_id], namespace=namespace)
        if "vectors" not in results or not results["vectors"]:
            return []
        return results["vectors"].values()

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
