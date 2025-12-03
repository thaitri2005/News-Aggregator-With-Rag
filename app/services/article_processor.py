# app/services/article_processor.py
from services.vector_db_service import VectorDBService, get_vectorizer
import logging
import re

logger = logging.getLogger(__name__)

class ArticleProcessor:
    def __init__(self):
        # Use singleton instances - these will be shared across all ArticleProcessor instances
        self.vector_db = VectorDBService()  # Singleton - creates vectorizer internally
        # Get the shared vectorizer instance from VectorDBService
        self.vectorizer = self.vector_db.vectorizer

    def process_and_store_article(self, article):
        """
        Processes an article by vectorizing its title and storing it in the vector database,
        with the content kept as metadata.
        """
        try:
            if not article.get('title') or not article.get('content'):
                logger.warning(f"Skipping article {article.get('source_url', 'unknown')} due to missing title or content.")
                return

            # Clean and preprocess title and content
            title = self.clean_text(article['title'])
            content = article['content']  # Keep raw content for metadata

            # Create and store vector for the title
            title_vector = self.create_title_vector(article, title, content)
            if title_vector:
                logger.debug(f"Upserting vector with metadata: {title_vector['metadata']}")
                self.vector_db.upsert_vectors([title_vector], namespace="title")
            else:
                logger.warning(f"Failed to create vector for title of article {article['source_url']}.")
        except Exception as e:
            logger.error(f"Error processing article {article.get('source_url', 'unknown')}: {e}")

    def clean_text(self, text):
        """
        Cleans the input text by removing special characters, extra spaces, and stop words.
        """
        try:
            if not text:
                return ""

            # stop_words = {"và", "nhưng", "hoặc", "cũng", "để", "đến", "là", "của", "có", "khi", "vì", "do", "nếu", "bởi", "đã"}
            text = re.sub(r"[^\w\s]", " ", text)  # Remove special characters
            text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
            words = text.split()
            cleaned_text = " ".join(word for word in words)
            logger.debug(f"Cleaned text: {cleaned_text[:200]}...")  # Log a sample of the cleaned text
            return cleaned_text
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text

    def create_title_vector(self, article, title, content):
        """
        Creates a vector representation for the article's title.
        """
        try:
            logger.info(f"Vectorizing title for article {article['source_url']}.")
            title_vector = self.vectorizer.encode_text(title)
            if title_vector is None or len(title_vector) != self.vectorizer.target_dim:
                logger.error(f"Invalid vector for title. Expected dimension: {self.vectorizer.target_dim}.")
                return None
            metadata = {
                'type': 'title',
                'title': title,
                'content': content,  # Full content stored in metadata
                'source_url': article['source_url'],
                # Ensure Pinecone metadata values are JSON-serializable primitives
                'date': (
                    article['date'].isoformat() if hasattr(article.get('date'), 'isoformat') else str(article.get('date'))
                ),
                'source': article['source'],
            }
            logger.debug(f"Generated metadata: {metadata}")
            return {
                'id': f"{article['source_url']}-title",
                'values': title_vector.tolist(),
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Failed to vectorize title for article {article['source_url']}: {e}")
            return None
