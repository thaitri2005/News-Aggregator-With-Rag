import logging
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up MongoDB connection
client = MongoClient('mongo', 27017)
db = client.newsdb
collection = db.articles

# Function to scrape the content from individual article pages
def scrape_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main content within the entry-content div
        content_div = soup.find('div', class_='entry-content wp-block-post-content is-layout-flow wp-block-post-content-is-layout-flow')
        
        # Extract all text within this div, or return "Content not found" if not found
        if content_div:
            content = content_div.get_text(separator="\n", strip=True)  # Use separator to keep paragraphs separate
            return content
        else:
            logger.warning(f"Content not found at {url}")
            return "Content not found"
    except requests.RequestException as e:
        logger.error(f"Error fetching content from {url}: {e}")
        return "Content not found"

# Main function to scrape TechCrunch
def scrape_techcrunch():
    url = "https://techcrunch.com/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching TechCrunch page: {e}")
        return

    articles = soup.find_all('article')
    new_articles = []

    for article in articles:
        # Find title and URL
        title_tag = article.find('h2')
        if not title_tag:
            logger.warning("No title found for an article, skipping.")
            continue
        
        # Extract title and link
        title = title_tag.get_text(strip=True)
        link_tag = title_tag.find('a', href=True)
        link = link_tag['href'] if link_tag else None

        if not link:
            logger.warning(f"Skipping article with title '{title}' because no link was found.")
            continue

        # Get the content from the article's page
        full_content = scrape_article_content(link)

        date = datetime.now()

        # Check for duplicate articles
        if collection.find_one({'title': title, 'source_url': link}):
            logger.info(f"Duplicate found for article '{title}', skipping.")
            continue

        # Insert the article into the database
        new_articles.append({
            'title': title,
            'content': full_content,
            'date': date,
            'source_url': link,
            'source': 'TechCrunch'
        })

    if new_articles:
        collection.insert_many(new_articles)
        logger.info(f"Inserted {len(new_articles)} new articles from TechCrunch.")
    else:
        logger.info("No new articles were added from TechCrunch.")

if __name__ == "__main__":
    scrape_techcrunch()
