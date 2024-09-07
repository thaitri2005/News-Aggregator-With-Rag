import logging
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up MongoDB connection
client = MongoClient('mongo', 27017)
db = client.newsdb
collection = db.articles

def scrape_guardian():
    url = 'https://www.theguardian.com/international'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching Guardian page: {e}")
        return

    articles = soup.find_all('div', class_='fc-item__container')
    new_articles = []

    article_urls = set()
    
    for article in articles:
        title = article.find('a').get_text(strip=True)
        link = article.find('a')['href']
        date = datetime.now()

        # Avoid duplicate articles based on URL
        if link in article_urls or collection.find_one({'title': title, 'source_url': link}):
            continue

        article_urls.add(link)

        content = fetch_article_content(link)
        if content:
            new_articles.append({
                'title': title,
                'content': content,
                'date': date,
                'source_url': link
            })
    
    if new_articles:
        collection.insert_many(new_articles)
        logger.info(f'Inserted {len(new_articles)} new articles from The Guardian.')
    else:
        logger.info("No new articles found for The Guardian.")

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
    scrape_guardian()
