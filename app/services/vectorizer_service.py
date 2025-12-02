#app/services/vectorizer_service.py
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import re
import logging

logger = logging.getLogger(__name__)

# Module-level singleton instance
_vectorizer_instance = None

def get_vectorizer(model_name='vinai/phobert-base', target_dim=768):
    """
    Get or create the singleton PhoBERTVectorizer instance.
    This ensures the model is only loaded once across the entire application.
    """
    global _vectorizer_instance
    if _vectorizer_instance is None:
        _vectorizer_instance = PhoBERTVectorizer(model_name, target_dim)
    return _vectorizer_instance

class PhoBERTVectorizer:
    def __init__(self, model_name='vinai/phobert-base', target_dim=768):
        """
        Initializes the PhoBERT vectorizer with the specified model and target dimension.
        Use get_vectorizer() function instead of direct instantiation to ensure singleton pattern.
        """
        print("Loading PhoBERT model... This may take a few minutes.")
        logger.info("Loading PhoBERT model... This may take a few minutes.")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.target_dim = target_dim  # Target dimension for embeddings
        print("PhoBERT model loaded successfully.")
        logger.info("PhoBERT model loaded successfully.")

    def encode_text(self, text):
        """
        Encodes a piece of text into a vector using PhoBERT and pads or resizes it.
        """
        # Clean text directly here (if needed)
        text = re.sub(r"[^\w\s]", " ", text)  # Example cleaning
        text = re.sub(r"\s+", " ", text).strip()

        inputs = self.tokenizer(text, truncation=True, max_length=512, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token's embedding (first token) for simplicity
            cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
        return self.pad_or_resize_embedding(cls_embedding)


    def pad_or_resize_embedding(self, embedding):
        """
        Pads or resizes the embedding to match the target dimension.
        """
        try:
            if len(embedding) >= self.target_dim:
                return embedding[:self.target_dim]
            return np.pad(embedding, (0, self.target_dim - len(embedding)), mode="constant")
        except Exception as e:
            # Handle errors in padding or resizing
            raise ValueError(f"Failed to pad or resize embedding: {e}")
