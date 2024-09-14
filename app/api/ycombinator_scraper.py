# app/api/ycombinator_scraper.py
import logging
import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    client = MongoClient(mongo_uri)
    db = client.newsdb
    collection = db.articles
else:
    logger.error("MONGO_URI is not set. Cannot connect to MongoDB.")
    collection = None  # Set collection to None during tests

# Domain-specific scrapers
def scrape_medium(soup):
    content = soup.find('article')
    if content:
        return "\n".join([p.get_text(strip=True) for p in content.find_all('p')])
    return None

def scrape_github(soup):
    content = soup.find('article')
    if content:
        return content.get_text(strip=True)
    return None

def scrape_generic(soup):
    paragraphs = soup.find_all(['p', 'div', 'pre', 'article'])
    content = "\n".join([p.get_text(strip=True) for p in paragraphs])
    if not content:
        content = soup.get_text(strip=True)[:1000]  # Fallback to page text if no content
    return content if content else None

# Mapping of domain-specific scrapers
domain_scrapers = {
    "medium.com": scrape_medium,
    "github.com": scrape_github,
}

def fetch_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Detect the domain
            domain = urlparse(url).netloc

            # Use a domain-specific scraper if available
            if domain in domain_scrapers:
                logger.info(f"Using domain-specific scraper for {domain}")
                content = domain_scrapers[domain](soup)
            else:
                logger.info(f"Using generic scraper for {domain}")
                content = scrape_generic(soup)

            if content:
                return content
            else:
                logger.warning(f"No content extracted from {url}")
                return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error when fetching {url}: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying ({attempt + 1}/{retries})...")
                time.sleep(2)
                continue
            else:
                return None
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error while fetching content from {url}")
            return None

def scrape_ycombinator():
    base_url = "https://news.ycombinator.com/"
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching Hacker News page: {e}")
        return

    articles = soup.find_all('tr', class_='athing')
    if not articles:
        logger.warning("No articles found on Hacker News.")
        return

    new_articles = []

    for article in articles:
        title_tag = article.find('span', class_='titleline')
        if not title_tag:
            logger.debug("No title found for an article, skipping.")
            continue

        title_link = title_tag.find('a')
        if not title_link:
            logger.debug("No link found in title, skipping.")
            continue

        title = title_link.get_text(strip=True)
        link = title_link['href']

        # Check if the link is relative, and if so, prepend the base URL
        if link.startswith("item?"):
            link = base_url + link

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

        # Fetch the content from the article link
        article_content = fetch_article_content(link)
        if not article_content:
            logger.warning(f"No content retrieved for article '{title}', skipping.")
            continue

        # Add the article to the list
        new_articles.append({
            'title': title,
            'content': article_content,
            'date': date,
            'source_url': link,
            'source': 'Hacker News'
        })

    if new_articles and collection is not None:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from Hacker News.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from Hacker News.")

if __name__ == "__main__":
    scrape_ycombinator()
