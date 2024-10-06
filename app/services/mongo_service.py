#app/services/mongo_service.py
from utils.common import get_mongo_collection
import logging

logger = logging.getLogger(__name__)

def save_articles(collection_name, articles):
    collection = get_mongo_collection('newsdb', collection_name)
    new_articles = []

    for article in articles:
        if collection.find_one({'title': article['title'], 'source_url': article['source_url']}):
            logger.info(f"Duplicate article '{article['title']}', skipping.")
            continue
        new_articles.append(article)

    if new_articles:
        collection.insert_many(new_articles)
        logger.info(f"Inserted {len(new_articles)} new articles.")
    else:
        logger.info("No new articles to add.")
