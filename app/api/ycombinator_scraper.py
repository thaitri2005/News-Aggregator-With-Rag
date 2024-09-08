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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    client = MongoClient(mongo_uri)
    db = client.newsdb
    collection = db.articles
else:
    logger.info("No MONGO_URI found. Skipping MongoDB connection (useful for testing).")
    collection = None  # Set collection to None during tests

# Domain-specific scrapers
def scrape_medium(soup):
    content = soup.find('article')
    if content:
        return "\n".join([p.get_text(strip=True) for p in content.find_all('p')])
    return "No content available"

def scrape_github(soup):
    content = soup.find('article')
    if content:
        return content.get_text(strip=True)
    return "No content available"

def scrape_generic(soup):
    paragraphs = soup.find_all(['p', 'div', 'pre', 'article'])
    content = "\n".join([p.get_text(strip=True) for p in paragraphs])
    if not content:
        content = soup.get_text(strip=True)[:1000]  # Fallback to page text if no content
    return content if content else "No content available"

# Mapping of domain-specific scrapers
domain_scrapers = {
    "medium.com": scrape_medium,
    "github.com": scrape_github,
}

def fetch_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx, 5xx)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Detect the domain
            domain = urlparse(url).netloc

            # Use a domain-specific scraper if available
            if domain in domain_scrapers:
                logger.info(f"Using domain-specific scraper for {domain}")
                return domain_scrapers[domain](soup)

            # Otherwise, use the generic scraper
            logger.info(f"Using generic scraper for {domain}")
            return scrape_generic(soup)
            
        except requests.exceptions.HTTPError as e:
            if attempt < retries - 1:
                logger.error(f"Error fetching article content from {url}: {e}. Retrying...")
                time.sleep(2)  # Wait before retrying
                continue
            else:
                logger.error(f"Error fetching article content from {url}: {e}")
                return "No content available"
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return "No content available"

def scrape_ycombinator():
    base_url = "https://news.ycombinator.com/"
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
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
            logger.warning("No title found for an article, skipping.")
            continue

        title_link = title_tag.find('a')
        if not title_link:
            logger.warning("No link found in title, skipping.")
            continue
        
        title = title_link.get_text(strip=True)
        link = title_link['href']
        
        # Check if the link is relative, and if so, prepend the base URL
        if link.startswith("item?"):
            link = base_url + link
        
        date = datetime.now()  # Hacker News doesn't provide an explicit date, so we use the current time.

        # Explicitly check if collection is not None
        if collection is not None and collection.find_one({'title': title, 'source_url': link}):
            logger.info(f"Duplicate found for article '{title}', skipping.")
            continue

        # Fetch the content from the article link
        article_content = fetch_article_content(link)

        # Insert the article into the database
        new_articles.append({
            'title': title,
            'content': article_content,
            'date': date,
            'source_url': link,
            'source': 'Hacker News'
        })

    if new_articles and collection is not None:
        collection.insert_many(new_articles)
        logger.info(f"Inserted {len(new_articles)} new articles from Hacker News.")
    else:
        logger.info("No new articles were added from Hacker News.")

if __name__ == "__main__":
    scrape_ycombinator()
