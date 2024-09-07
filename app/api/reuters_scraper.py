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

def scrape_reuters():
    url = 'https://www.reuters.com/world/'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching Reuters page: {e}")
        return

    articles = soup.find_all('article', class_='story')
    new_articles = []

    for article in articles:
        title_tag = article.find('h3')
        if not title_tag:
            logger.warning("No title found for an article, skipping.")
            continue
        
        title = title_tag.get_text(strip=True)
        link_tag = article.find('a', href=True)
        link = link_tag['href'] if link_tag else None
        
        if not link:
            logger.warning(f"Skipping article with title '{title}' because no link was found.")
            continue
        
        full_link = f'https://www.reuters.com{link}' if not link.startswith('http') else link
        date = datetime.now()

        # Check for duplicate articles
        if collection.find_one({'title': title, 'source_url': full_link}):
            logger.info(f"Duplicate found for article '{title}', skipping.")
            continue

        content = fetch_article_content(full_link)
        if content:
            new_articles.append({
                'title': title,
                'content': content,
                'date': date,
                'source_url': full_link
            })

    if new_articles:
        collection.insert_many(new_articles)
        logger.info(f"Inserted {len(new_articles)} new articles from Reuters.")
    else:
        logger.info("No new articles were added from Reuters.")

def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text(strip=True) for para in paragraphs])
        return content
    except requests.RequestException as e:
        logger.error(f"Error fetching content from {url}: {e}")
        return None

if __name__ == "__main__":
    scrape_reuters()
