#services/article_processor.py
from services.vectorizer_service import PhoBERTVectorizer
from services.vector_db_service import VectorDBService
import logging

logger = logging.getLogger(__name__)

class ArticleProcessor:
    def __init__(self):
        self.vectorizer = PhoBERTVectorizer()
        self.vector_db = VectorDBService()

    def process_and_store_article(self, article):
        """
        Processes an article by chunking, vectorizing, and storing it in the vector database.
        """
        if not article.get('content'):
            logger.warning(f"Skipping article {article['source_url']} due to empty content.")
            return

        chunks = self.chunk_article(article['content'])
        if not chunks:
            logger.warning(f"No valid chunks created for article {article['source_url']}.")
            return

        vectors = self.create_vectors(article, chunks)
        if vectors:
            self.vector_db.upsert_vectors(vectors)
        else:
            logger.warning(f"No vectors created for article {article['source_url']}.")


    def chunk_article(self, content, chunk_size=500, overlap=100):
        """
        Splits article content into smaller chunks with optional overlap.
        """
        chunks = []
        for i in range(0, len(content), chunk_size - overlap):
            chunks.append(content[i:i + chunk_size])
        return chunks


    def create_vectors(self, article, chunks):
        """
        Creates vector representations for each chunk and prepares them for insertion into the vector database.
        """
        vectors = []
        for idx, chunk in enumerate(chunks):
            try:
                vector = self.vectorizer.encode_text(chunk)
                vectors.append({
                    'id': f"{article['source_url']}-{idx}",  # Unique ID for each chunk
                    'values': vector.tolist(),
                    'metadata': {
                        'title': article['title'],
                        'source_url': article['source_url'],
                        'date': article['date'].isoformat(),
                        'source': article['source'],
                        'chunk': chunk,
                    }
                })
            except Exception as e:
                logger.error(f"Failed to vectorize chunk {idx} for article {article['source_url']}: {e}")
        return vectors

