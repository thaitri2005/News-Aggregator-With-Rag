import logging
import os
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables")

    client = MongoClient(mongo_uri)
    db = client.newsdb
    return db.articles

# Article class for holding article information
class Article:
    def __init__(self, title, link, content, date):
        self.title = title
        self.link = link
        self.content = content
        self.date = date  # Article date

# Function to fetch article body/content and date from each article link
def fetch_article_content_and_date(link):
    try:
        session = requests.Session()
        response = session.get(link)

        if response.status_code != 200:
            logger.error(f"Failed to fetch article: {link}, status code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the main article content
        article_content = soup.select("article.fck_detail p.Normal")

        # Combine all paragraphs into a single content string
        content = "\n".join([p.get_text(strip=True) for p in article_content if p.text])

        if not content:
            logger.warning(f"Content not found for {link}")
            return None, None

        # Extract the publication date
        date_tag = soup.find("span", class_="date")
        if date_tag:
            date_str = date_tag.get_text(strip=True)
            # Parse the date string into a datetime object
            try:
                # Example date format: "Thứ năm, 3/10/2024, 11:53 (GMT+7)"
                # Remove 'GMT' part and any extra whitespace
                date_str = date_str.split(' (GMT')[0].strip()
                # Remove the weekday (e.g., 'Thứ năm,') part
                date_parts = date_str.split(', ')
                if len(date_parts) >= 2:
                    date_str = ', '.join(date_parts[1:])  # Get '3/10/2024, 11:53'
                    article_date = datetime.strptime(date_str, '%d/%m/%Y, %H:%M')
                else:
                    logger.warning(f"Unexpected date format for {link}: {date_str}")
                    article_date = None
            except ValueError as ve:
                logger.warning(f"Failed to parse date for {link}: {date_str}")
                article_date = None
        else:
            logger.warning(f"Date not found for {link}")
            article_date = None

        return content, article_date

    except Exception as e:
        logger.error(f"Error fetching article content and date from {link}: {str(e)}")
        return None, None

# Scrape articles using requests and BeautifulSoup
def get_news(limit_news=50):
    base_url = "https://vnexpress.net/"
    session = requests.Session()
    response = session.get(base_url)

    if response.status_code != 200:
        logger.error(f"Failed to fetch VNExpress page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Select articles from the main page
    articles = soup.select("article.item-news")

    list_articles = []
    for element in articles:
        title_tag = element.select_one("h3.title-news > a")
        link = title_tag['href'] if title_tag else None

        if title_tag and link:
            title = title_tag['title'].strip()
            logger.info(f"Fetching content from {link}")
            content, article_date = fetch_article_content_and_date(link)

            if content and article_date:
                # Create an Article object with title, link, content, and date
                list_articles.append(Article(
                    title=title,
                    link=link,
                    content=content,
                    date=article_date
                ))

    return list_articles

# Save articles to MongoDB
def save_to_mongo(articles):
    collection = get_mongo_collection()
    new_articles = []

    for article in articles:
        # Check for duplicates based on title and source URL (link)
        if collection.find_one({'title': article.title, 'source_url': article.link}):
            logger.info(f"Duplicate found for article '{article.title}', skipping.")
            continue

        # Save in the desired format
        new_articles.append({
            'title': article.title,
            'content': article.content,
            'date': article.date,  # Use the actual article date
            'source_url': article.link,
            'source': 'VNExpress'
        })

    if new_articles:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from VNExpress.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from VNExpress.")

# Main function to run the scraper
def scrape_vnexpress():
    logger.info("Starting VNExpress scraper...")
    articles = get_news(limit_news=50)

    if not articles:
        logger.warning("No articles found on VNExpress.")
        return

    save_to_mongo(articles)
    logger.info("VNExpress scraper completed.")

if __name__ == "__main__":
    scrape_vnexpress()
