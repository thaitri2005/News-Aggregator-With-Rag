# app/models/article_model.py
from datetime import datetime

class Article:
    def __init__(self, title, content, source_url, date=None, source=""):
        self.title = title
        self.content = content
        self.source_url = source_url
        self.date = date or datetime.utcnow()
        self.source = source

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "date": self.date,
            "source": self.source
        }
