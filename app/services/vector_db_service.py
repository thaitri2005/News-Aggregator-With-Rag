# app/services/vector_db_service.py
from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeException, PineconeApiException
from services.vectorizer_service import get_vectorizer
import os
import logging
import re
import time

logger = logging.getLogger(__name__)

class VectorDBService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """
        Singleton pattern: ensures only one instance of VectorDBService exists.
        """
        if cls._instance is None:
            cls._instance = super(VectorDBService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once due to singleton pattern
        if VectorDBService._initialized:
            return
            
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", "aggsum")
        dimension = int(os.getenv("PINECONE_DIMENSION", "768"))  # PhoBERT dimension
        pinecone_region = os.getenv("PINECONE_REGION", "us-east-1")  # Default AWS region

        if not api_key:
            raise ValueError("PINECONE_API_KEY must be set in the environment variables.")

        logger.info(f"Initializing Pinecone connection to index: {index_name}")
        self.pinecone = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.pinecone_region = pinecone_region
        
        # Check if index exists, create if it doesn't
        self._ensure_index_exists(dimension)
        
        # Connect to the index
        self.index = self.pinecone.Index(index_name)

        # Initialize PhoBERT for encoding (singleton, so only loads once)
        self.vectorizer = get_vectorizer()
        VectorDBService._initialized = True
    
    def _ensure_index_exists(self, dimension=768):
        """
        Checks if the Pinecone index exists, and creates it if it doesn't.
        """
        try:
            # List all indexes
            existing_indexes = [idx.name for idx in self.pinecone.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Index '{self.index_name}' not found. Creating new index with dimension {dimension}...")
                
                # Create the index (serverless)
                try:
                    self.pinecone.create_index(
                        name=self.index_name,
                        dimension=dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region=self.pinecone_region
                        )
                    )
                    logger.info(f"Index '{self.index_name}' creation initiated (serverless). Waiting for it to be ready...")
                    self._wait_for_index_ready()
                except PineconeApiException as e:
                    # Check if index already exists (race condition or concurrent creation)
                    if hasattr(e, 'status_code') and e.status_code == 409:
                        logger.info(f"Index '{self.index_name}' already exists (created concurrently or exists).")
                        self._wait_for_index_ready()
                    else:
                        logger.error(f"Failed to create index: {e}")
                        logger.error("Please create the index manually in Pinecone console or check your API key permissions.")
                        logger.warning("Attempting to proceed with existing index connection...")
                except Exception as e:
                    # Handle other exceptions
                    error_str = str(e).lower()
                    if "already exists" in error_str or "409" in error_str:
                        logger.info(f"Index '{self.index_name}' already exists.")
                        self._wait_for_index_ready()
                    else:
                        logger.error(f"Failed to create index: {e}")
                        logger.warning("Attempting to proceed with existing index connection...")
            else:
                logger.info(f"Index '{self.index_name}' already exists.")
                # Verify index is ready
                self._wait_for_index_ready()
        except Exception as e:
            logger.error(f"Error checking/creating index: {e}")
            # If we can't create, try to connect anyway (might already exist)
            logger.warning("Attempting to connect to existing index...")
    
    def _wait_for_index_ready(self, max_wait_time=300):
        """
        Waits for the index to be ready, polling every 5 seconds.
        """
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                index_description = self.pinecone.describe_index(self.index_name)
                if hasattr(index_description, 'status') and index_description.status.get('ready', False):
                    logger.info(f"Index '{self.index_name}' is ready!")
                    return
                elif hasattr(index_description, 'status'):
                    logger.info(f"Index status: {index_description.status}")
            except Exception as e:
                logger.debug(f"Waiting for index to be ready: {e}")
            
            time.sleep(5)
        
        logger.warning(f"Index '{self.index_name}' may not be ready yet, but proceeding anyway...")

    @staticmethod
    def clean_text(text):
        """
        Cleans the input text by removing Vietnamese stop words, symbols, and excess spaces.
        """
        try:
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
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text

    def upsert_vectors(self, vectors, namespace="default"):
        """
        Upserts a batch of vectors to Pinecone.
        """
        if not vectors:
            logger.warning("No vectors to upsert.")
            return
        try:
            logger.info(f"Upserting {len(vectors)} vectors to namespace '{namespace}'...")
            response = self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Upsert successful. Response: {response}")
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            raise

    def query_vectors(self, query, namespace="default", top_k=5):
        """
        Queries the Pinecone index for top-k similar vectors.
        """
        try:
            query = self.clean_text(query)  # Clean the query text
            query_vector = self.vectorizer.encode_text(query)
            if query_vector is None:
                logger.error("Failed to vectorize the query.")
                return []

            query_vector = query_vector.tolist()

            logger.info(f"Querying Pinecone with cleaned query: '{query[:200]}...' (namespace: {namespace})")
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
            )

            matches = [
                {"id": match["id"], "score": match["score"], "metadata": match["metadata"]}
                for match in response.get("matches", [])
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
            logger.info(f"Fetching vector for ID: {article_id} (namespace: {namespace})")
            results = self.index.fetch(ids=[article_id], namespace=namespace)
            vectors = results.get("vectors", {})
            if not vectors:
                logger.warning(f"No results found for ID: {article_id}")
                return []
            return vectors.values()
        except Exception as e:
            logger.error(f"Error fetching vector by ID: {e}")
            raise

    def query_by_title(self, title, namespace="default", top_k=5):
        """
        Queries the Pinecone index for vectors most similar to the given title.
        """
        try:
            title = self.clean_text(title)  # Clean the title text
            title_vector = self.vectorizer.encode_text(title)
            if title_vector is None:
                logger.error("Failed to vectorize the title.")
                return []

            title_vector = title_vector.tolist()

            logger.info(f"Querying Pinecone with title vector for: '{title[:200]}...' (namespace: {namespace})")
            response = self.index.query(
                vector=title_vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
            )

            matches = [
                {"id": match["id"], "score": match["score"], "metadata": match["metadata"]}
                for match in response.get("matches", [])
            ]
            logger.info(f"Found {len(matches)} matches for title query.")
            return matches
        except Exception as e:
            logger.error(f"Title query failed: {e}")
            raise

    def delete_all(self, namespace="default"):
        """
        Deletes all vectors in a given namespace using the Pinecone `delete` method.
        """
        try:
            logger.info(f"Deleting all vectors in namespace '{namespace}'...")
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Successfully deleted all vectors in namespace '{namespace}'.")
        except Exception as e:
            logger.error(f"Failed to delete all vectors in namespace '{namespace}': {e}")
            raise
