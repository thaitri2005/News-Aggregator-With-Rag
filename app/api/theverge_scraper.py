import logging
import os
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import json
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up MongoDB connection only if MONGO_URI is set
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    client = MongoClient(mongo_uri)
    db = client.newsdb
    collection = db.articles
else:
    # Use a mock collection for local tests
    collection = None

def scrape_theverge():
    base_url = "https://www.theverge.com"
    homepage_url = base_url

    try:
        response = requests.get(homepage_url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Log the first part of the HTML to verify structure
        logger.info(soup.prettify()[:500])

    except requests.RequestException as e:
        logger.error(f"Error fetching The Verge homepage: {e}")
        return

    articles = soup.find_all('a', class_='text-black hover:text-blurple')
    
    if not articles:
        logger.warning("No articles found on The Verge homepage. HTML structure may have changed.")
    
    new_articles = []

    for article in articles:
        title = article.get_text(strip=True)
        link = article['href'] if article.has_attr('href') else None

        if not title or title.lower() == "comments":
            logger.warning(f"Skipping article due to missing or irrelevant title: '{title}'")
            continue

        if not link:
            logger.warning(f"Skipping article with title '{title}' because no link was found.")
            continue

        if link.startswith("/"):
            link = base_url + link

        full_content = fetch_article_content(link)
        if not full_content:
            logger.warning(f"No content found for article '{title}', skipping.")
            continue

        date = datetime.now()

        # Check if collection exists before querying
        if collection is not None and collection.find_one({'title': title, 'source_url': link}):
            logger.info(f"Duplicate found for article '{title}', skipping.")
            continue

        new_articles.append({
            'title': title,
            'content': full_content,
            'date': date,
            'source_url': link,
            'source': 'The Verge'
        })

    if new_articles and collection is not None:
        collection.insert_many(new_articles)
        logger.info(f"Inserted {len(new_articles)} new articles from The Verge.")
    else:
        logger.info("No new articles were added from The Verge.")


def fetch_article_content(link):
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        logger.info(f"Fetching content from {link}")
        ld_json_script = soup.find('script', type='application/ld+json')
        if not ld_json_script:
            logger.warning(f"No JSON-LD script tag found for {link}")
            return None
        
        try:
            article_data = json.loads(ld_json_script.string)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {link}: {e}")
            return None

        article_body = article_data.get("articleBody", "")
        if not article_body:
            logger.warning(f"No article body found in JSON for {link}")
            return None

        logger.info(f"Article body found for {link}: {article_body[:200]}...")
        return article_body
    except requests.RequestException as e:
        logger.error(f"Error fetching article content from {link}: {e}")
        return None
