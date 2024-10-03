# app/api/tuoitre_scraper.py
import logging
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
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

        # Fetch content from updated HTML structure
        content_div = soup.find('div', class_='detail-content afcbc-body')
        if content_div:
            # Extract all paragraphs within the article content
            paragraphs = content_div.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
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

# Function to extract articles from both original and additional sections
def extract_article_links(soup):
    base_url = "https://tuoitre.vn"
    
    # Original section scraping
    original_articles = soup.select('div.swiper-slide .box-category-link-title')
    
    # Additional sections scraping
    additional_articles = soup.select('div.box-category-item a.box-category-link-title')
    
    # Combine both article sets
    all_articles = original_articles + additional_articles

    article_links = []
    for article in all_articles:
        title = article.get_text(strip=True)
        link = article['href']

        if not link.startswith('http'):
            link = base_url + link

        article_links.append({'title': title, 'link': link})

    return article_links

# Main function to scrape Tuổi Trẻ
def scrape_tuoitre():
    base_url = "https://tuoitre.vn"
    
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching Tuổi Trẻ page: {e}")
        return

    # Extract article links from both the original and additional sections
    articles = extract_article_links(soup)
    if not articles:
        logger.warning("No articles found on Tuổi Trẻ.")
        return

    new_articles = []
    collection = get_mongo_collection()

    for article in articles:
        title = article['title']
        link = article['link']

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
            'source': 'Tuổi Trẻ'
        })

    if new_articles:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from Tuổi Trẻ.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from Tuổi Trẻ.")

if __name__ == "__main__":
    scrape_tuoitre()
