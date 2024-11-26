#services/article_processor.py
from services.vectorizer_service import PhoBERTVectorizer
from services.vector_db_service import VectorDBService

class ArticleProcessor:
    def __init__(self):
        self.vectorizer = PhoBERTVectorizer()
        self.vector_db = VectorDBService()

    def process_and_store_article(self, article):
        """
        Processes an article by chunking, vectorizing, and storing it in the vector database.
        """
        chunks = self.chunk_article(article['content'])
        vectors = self.create_vectors(article, chunks)
        self.vector_db.upsert_vectors(vectors)

    def chunk_article(self, content, chunk_size=500):
        """
        Splits article content into smaller chunks.
        """
        return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    def create_vectors(self, article, chunks):
        """
        Creates vector representations for each chunk and prepares them for insertion into the vector database.
        """
        vectors = []
        for idx, chunk in enumerate(chunks):
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
        return vectors
