import logging
import os
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables")

    client = MongoClient(mongo_uri)
    db = client.newsdb
    return db.articles

# Article class for holding article information
class Article:
    def __init__(self, title, link, content):
        self.title = title
        self.link = link
        self.content = content

# Function to fetch article body/content from each article link
def fetch_article_content(link):
    try:
        session = requests.Session()
        response = session.get(link)

        if response.status_code != 200:
            logger.error(f"Failed to fetch article: {link}, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the article content
        article_content = soup.select("div.maincontent p")

        # Combine all paragraphs into a single content string
        content = "\n".join([p.text for p in article_content if p.text])

        if not content:
            logger.warning(f"Content not found for {link}")
            return None

        return content

    except Exception as e:
        logger.error(f"Error fetching article content from {link}: {str(e)}")
        return None

# Scrape articles using requests and BeautifulSoup
def get_news(limit_news=20):
    base_url = "https://vietnamnet.vn/"
    session = requests.Session()
    response = session.get(base_url)

    if response.status_code != 200:
        logger.error(f"Failed to fetch VietnamNet page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Select articles from the main page
    articles = soup.select("div.horizontalPost a")[:limit_news]

    list_articles = []
    for element in articles:
        title = element.get('title')
        link = base_url.strip("/") + element.get('href')

        if title and link:
            logger.info(f"Fetching content from {link}")
            content = fetch_article_content(link)

            if content:
                # Create an Article object with title, link, and content
                list_articles.append(Article(
                    title=title,
                    link=link,
                    content=content
                ))

    return list_articles

# Save articles to MongoDB
def save_to_mongo(articles):
    collection = get_mongo_collection()
    new_articles = []

    for article in articles:
        # Check for duplicates based on title and source URL (link)
        if collection.find_one({'title': article.title, 'source_url': article.link}):
            logger.info(f"Duplicate found for article '{article.title}', skipping.")
            continue

        # Save in the desired format
        new_articles.append({
            'title': article.title,
            'content': article.content,
            'date': datetime.now(),  # Current date when saving
            'source_url': article.link,  # Storing the link as source_url
            'source': 'VietnamNet'  # You can modify the source as needed
        })

    if new_articles:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from VietnamNet.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from VietnamNet.")

# Main function to run the scraper
def scrape_vietnamnet():
    logger.info("Starting VietnamNet scraper...")
    articles = get_news(limit_news=20)

    if not articles:
        logger.warning("No articles found on VietnamNet.")
        return

    save_to_mongo(articles)
    logger.info("VietnamNet scraper completed.")

# For testing purposes, you can call this function directly
if __name__ == "__main__":
    scrape_vietnamnet()
