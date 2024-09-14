# app/api/theverge_scraper.py
import logging
import os
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Set up MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    client = MongoClient(mongo_uri)
    db = client.newsdb
    collection = db.articles
else:
    logger.error("MONGO_URI is not set. Cannot connect to MongoDB.")
    collection = None

def scrape_theverge():
    base_url = "https://www.theverge.com"

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching The Verge homepage: {e}")
        return

    # Find articles
    articles = soup.find_all('a', class_='text-black hover:text-blurple')
    if not articles:
        logger.warning("No articles found on The Verge homepage. HTML structure may have changed.")
        return

    new_articles = []

    for article in articles:
        title = article.get_text(strip=True)
        link = article.get('href')

        if not title or title.lower() == "comments":
            logger.debug(f"Skipping article due to missing or irrelevant title: '{title}'")
            continue

        if not link:
            logger.debug(f"Skipping article with title '{title}' because no link was found.")
            continue

        if link.startswith("/"):
            link = base_url + link

        full_content = fetch_article_content(link)
        if not full_content:
            logger.warning(f"No content found for article '{title}', skipping.")
            continue

        date = datetime.now()

        # Check for duplicates
        if collection is not None:
            try:
                if collection.find_one({'title': title, 'source_url': link}):
                    logger.info(f"Duplicate found for article '{title}', skipping.")
                    continue
            except Exception as e:
                logger.exception("Failed to query the database for duplicates.")
                continue

        new_articles.append({
            'title': title,
            'content': full_content,
            'date': date,
            'source_url': link,
            'source': 'The Verge'
        })

    if new_articles and collection is not None:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from The Verge.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from The Verge.")

def fetch_article_content(link):
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        logger.info(f"Fetching content from {link}")
        ld_json_scripts = soup.find_all('script', type='application/ld+json')

        article_body = None
        for script in ld_json_scripts:
            try:
                article_data = json.loads(script.string)
                if article_data.get("@type") == "NewsArticle":
                    article_body = article_data.get("articleBody", "")
                    break
            except (json.JSONDecodeError, TypeError) as e:
                logger.debug(f"Error decoding JSON from {link}: {e}")
                continue

        if not article_body:
            logger.warning(f"No article body found in JSON for {link}")
            return None

        logger.debug(f"Article body found for {link}: {article_body[:200]}...")
        return article_body
    except requests.Timeout:
        logger.error(f"Timeout error when fetching content from {link}")
        return None
    except requests.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} when fetching content from {link}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred when fetching content from {link}")
        return None

if __name__ == "__main__":
    scrape_theverge()
