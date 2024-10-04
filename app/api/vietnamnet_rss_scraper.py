import feedparser
import logging
import os
import requests
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

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

# VietnamNet RSS Feeds
RSS_FEEDS = {
    "Đời sống": "https://infonet.vietnamnet.vn/rss/doi-song.rss",
    "Thị trường": "https://infonet.vietnamnet.vn/rss/thi-truong.rss",
    "Thế giới": "https://infonet.vietnamnet.vn/rss/the-gioi.rss",
    "Gia đình": "https://infonet.vietnamnet.vn/rss/gia-dinh.rss",
    "Giới trẻ": "https://infonet.vietnamnet.vn/rss/gioi-tre.rss",
    "Khỏe - Đẹp": "https://infonet.vietnamnet.vn/rss/khoe-dep.rss",
    "Chuyện lạ": "https://infonet.vietnamnet.vn/rss/chuyen-la.rss",
    "Quân sự": "https://infonet.vietnamnet.vn/rss/quan-su.rss"
}

# Function to clean HTML content
def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator="\n").strip()
    return text

# Function to extract image from the description if present
def extract_image(description):
    soup = BeautifulSoup(description, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    return None

# Function to fetch article body/content from each article link
# Function to fetch article body/content from each article link
def fetch_article_content(link):
    try:
        session = requests.Session()
        response = session.get(link)

        if response.status_code != 200:
            logger.error(f"Failed to fetch article: {link}, status code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the main article content based on the provided HTML structure
        main_content = soup.select_one("div.contentDetail__main-reading")

        if not main_content:
            logger.warning(f"Main content not found for {link}")
            return None, None

        # Extract paragraphs inside the main content
        paragraphs = main_content.find_all('p')
        content = "\n".join([p.text for p in paragraphs if p.text])

        # Locate the publish date if available (you may need to adjust this based on actual HTML)
        publish_date = soup.select_one("div.publish-date")
        if publish_date:
            date_str = publish_date.text.strip().split()[0]
            try:
                date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                logger.warning(f"Date parsing failed for {link}, using current datetime.")
                date = datetime.now()
        else:
            logger.warning(f"Date not found for {link}, using current datetime.")
            date = datetime.now()

        if not content:
            logger.warning(f"Content not found for {link}")
            return None, date

        return content, date

    except Exception as e:
        logger.error(f"Error fetching article content from {link}: {str(e)}")
        return None, None

# Function to fetch articles from a given RSS feed URL
def fetch_rss_articles(feed_name, feed_url):
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            summary = clean_html(entry.summary)
            published_date = entry.published

            try:
                # Convert published_date to a datetime object
                date_obj = datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %z')
            except ValueError as e:
                logger.error(f"Date parsing failed for {published_date}: {e}")
                continue  # Skip this article if the date can't be parsed

            # Fetch full article content
            full_content, article_date = fetch_article_content(link)

            if full_content:
                articles.append({
                    "title": title,
                    "content": full_content,
                    "source_url": link,
                    "date": article_date or date_obj,  # Use article_date if available, otherwise use RSS date
                    "source": f"VietnamNet - {feed_name}"
                })

        return articles
    except Exception as e:
        logger.exception(f"Failed to fetch articles from RSS feed {feed_name}: {e}")
        return []

# Save articles to MongoDB
def save_to_mongo(articles):
    collection = get_mongo_collection()
    new_articles = []

    for article in articles:
        if collection.find_one({'title': article['title'], 'source_url': article['source_url']}):
            logger.info(f"Duplicate found for article '{article['title']}', skipping.")
            continue

        new_articles.append(article)

    if new_articles:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from VietnamNet RSS.")
        except Exception as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from VietnamNet RSS.")

# Main function to run the RSS scraper for multiple feeds
def scrape_vietnamnet_rss():
    logger.info("Starting VietnamNet RSS scraper...")

    for feed_name, feed_url in RSS_FEEDS.items():
        logger.info(f"Fetching articles from {feed_name} feed...")
        articles = fetch_rss_articles(feed_name, feed_url)

        if not articles:
            logger.warning(f"No articles found in {feed_name} RSS feed.")
            continue

        save_to_mongo(articles)

    logger.info("VietnamNet RSS scraper completed.")

# For testing purposes, you can call this function directly
if __name__ == "__main__":
    scrape_vietnamnet_rss()
