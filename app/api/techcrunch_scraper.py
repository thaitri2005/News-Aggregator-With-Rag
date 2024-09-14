# app/api/techcrunch_scraper.py
import logging
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger(__name__)

def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables")
    
    client = MongoClient(mongo_uri)
    db = client.newsdb
    return db.articles

# Function to scrape the content from individual article pages
def scrape_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        content_div = soup.find('div', class_='article-content')
        if content_div:
            content = content_div.get_text(separator="\n", strip=True)
            return content
        else:
            logger.warning(f"Content not found at {url}")
            return None
    except requests.Timeout:
        logger.error(f"Timeout error when fetching content from {url}")
        return None
    except requests.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} when fetching content from {url}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred when fetching content from {url}")
        return None

# Main function to scrape TechCrunch
def scrape_techcrunch():
    base_url = "https://techcrunch.com"
    
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching TechCrunch page: {e}")
        return

    articles = soup.find_all('article')
    if not articles:
        logger.warning("No articles found on TechCrunch.")
        return

    new_articles = []
    collection = get_mongo_collection()

    for article in articles:
        title_tag = article.find('h2')
        if not title_tag:
            logger.warning("No title found for an article, skipping.")
            continue

        title = title_tag.get_text(strip=True)
        link_tag = title_tag.find('a', href=True)
        link = link_tag['href'] if link_tag else None

        if not link:
            logger.warning(f"Skipping article with title '{title}' because no link was found.")
            continue

        if link.startswith('/'):
            link = base_url + link

        logger.info(f"Fetching content from {link}")

        full_content = scrape_article_content(link)
        if not full_content:
            logger.warning(f"No content retrieved for article '{title}', skipping.")
            continue

        date = datetime.now()

        if collection.find_one({'title': title, 'source_url': link}):
            logger.info(f"Duplicate found for article '{title}', skipping.")
            continue

        new_articles.append({
            'title': title,
            'content': full_content,
            'date': date,
            'source_url': link,
            'source': 'TechCrunch'
        })

    if new_articles:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from TechCrunch.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from TechCrunch.")
