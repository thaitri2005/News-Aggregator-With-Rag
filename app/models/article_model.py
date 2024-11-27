# app/models/article_model.py
from datetime import datetime
import re

class Article:
    def __init__(self, title, content, source_url, date=None, source=""):
        """
        Represents an article with title, full content, source information, and metadata.
        """
        self.title = self.clean_text(title) if title else "Untitled"
        self.content = self.clean_text(content) if content else ""
        self.source_url = source_url
        self.date = date or datetime.utcnow()
        self.source = self.clean_text(source) if source else "Unknown"

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "date": self.date,
            "source": self.source,
        }

    def validate(self):
        """
        Validates the Article fields to ensure completeness and correctness.
        """
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Title must be a non-empty string.")
        if not self.content or not isinstance(self.content, str):
            raise ValueError("Content must be a non-empty string.")
        if not self.source_url or not isinstance(self.source_url, str):
            raise ValueError("Source URL must be a valid URL string.")
        if not isinstance(self.date, (datetime, str)):
            raise ValueError("Date must be a datetime object or ISO8601 string.")
        if not self.source or not isinstance(self.source, str):
            raise ValueError("Source must be a string.")

    @staticmethod
    def clean_text(text):
        """
        Cleans the input text by removing unnecessary symbols and normalizing whitespace.
        """
        text = re.sub(r"[^\w\s]", " ", text)  # Remove special characters
        text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
        return text
