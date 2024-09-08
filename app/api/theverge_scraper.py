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

# Set up MongoDB connection using MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in the environment variables")

client = MongoClient(mongo_uri)
db = client.newsdb
collection = db.articles

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

    # Updated selector to match the current HTML structure
    articles = soup.find_all('a', class_='text-black hover:text-blurple')
    
    if not articles:
        logger.warning("No articles found on The Verge homepage. HTML structure may have changed.")
    
    new_articles = []

    for article in articles:
        title = article.get_text(strip=True)
        link = article['href'] if article.has_attr('href') else None

        # Skip articles that don't have a title or have 'Comments' as the title
        if not title or title.lower() == "comments":
            logger.warning(f"Skipping article due to missing or irrelevant title: '{title}'")
            continue

        if not link:
            logger.warning(f"Skipping article with title '{title}' because no link was found.")
            continue

        # Ensure the link has the full URL
        if link.startswith("/"):
            link = base_url + link

        # Fetch full article content
        full_content = fetch_article_content(link)
        if not full_content:
            logger.warning(f"No content found for article '{title}', skipping.")
            continue

        date = datetime.now()  # The Verge homepage doesn't provide the publication date, so use the current time.

        # Check for duplicate articles in the database
        if collection.find_one({'title': title, 'source_url': link}):
            logger.info(f"Duplicate found for article '{title}', skipping.")
            continue

        # Insert the article into the database
        new_articles.append({
            'title': title,
            'content': full_content,
            'date': date,
            'source_url': link,
            'source': 'The Verge'
        })

    if new_articles:
        collection.insert_many(new_articles)
        logger.info(f"Inserted {len(new_articles)} new articles from The Verge.")
    else:
        logger.info("No new articles were added from The Verge.")


def fetch_article_content(link):
    """
    Fetch the full content of the article by visiting its URL and parsing 
    it from the <script type="application/ld+json"> section.
    """
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Log the URL for reference
        logger.info(f"Fetching content from {link}")
        
        # Find the <script> tag containing the article's JSON-LD data
        ld_json_script = soup.find('script', type='application/ld+json')
        if not ld_json_script:
            logger.warning(f"No JSON-LD script tag found for {link}")
            return None
        
        # Parse the JSON content
        try:
            article_data = json.loads(ld_json_script.string)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {link}: {e}")
            return None

        # Extract the article body from the JSON
        article_body = article_data.get("articleBody", "")
        if not article_body:
            logger.warning(f"No article body found in JSON for {link}")
            return None
        
        # Optionally log part of the content for verification
        logger.info(f"Article body found for {link}: {article_body[:200]}...")  # Log first 200 chars
        
        return article_body
    except requests.RequestException as e:
        logger.error(f"Error fetching article content from {link}: {e}")
        return None


if __name__ == "__main__":
    scrape_theverge()
