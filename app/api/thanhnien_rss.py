import feedparser
import logging
from pymongo.errors import PyMongoError
from datetime import datetime
from bs4 import BeautifulSoup
from tuoitre_scraper import get_mongo_collection  # Import the existing get_mongo_collection function

logger = logging.getLogger(__name__)

# List of RSS Feed URLs for Thanh Niên
RSS_FEEDS = {
    "Trang Chủ": "https://thanhnien.vn/rss/home.rss"
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

# Function to fetch articles from a given RSS feed URL
def fetch_rss_articles(feed_name, feed_url):
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            published_date = entry.published
            summary = entry.summary

            clean_content = clean_html(summary)
            image_url = extract_image(summary)

            try:
                date_obj = datetime.strptime(published_date, '%a, %d %b %y %H:%M:%S %z')
            except ValueError as e:
                logger.error(f"Date parsing failed for {published_date}: {e}")
                continue  # Skip this article if the date can't be parsed

            articles.append({
                "title": title,
                "content": clean_content,
                # "image_url": image_url,
                "source_url": link,
                "date": date_obj,
                "source": f"Thanh Niên - {feed_name}"
            })

        return articles
    except Exception as e:
        logger.exception(f"Failed to fetch articles from RSS feed {feed_name}: {e}")
        return []

# Save articles to MongoDB
def save_to_mongo(articles):
    collection = get_mongo_collection()  # Correctly initialize the collection

    new_articles = []
    for article in articles:
        if collection.find_one({'title': article['title'], 'source_url': article['source_url']}):
            logger.info(f"Duplicate found for article '{article['title']}', skipping.")
            continue

        new_articles.append(article)

    if new_articles:
        try:
            collection.insert_many(new_articles)
            logger.info(f"Inserted {len(new_articles)} new articles from RSS feed.")
        except PyMongoError as e:
            logger.exception("Failed to insert new articles into the database.")
    else:
        logger.info("No new articles were added from RSS feed.")

# Main function to run the RSS scraper for multiple feeds
def rss_thanhnien():
    logger.info("Starting RSS scraper for Thanh Niên...")

    for feed_name, feed_url in RSS_FEEDS.items():
        logger.info(f"Fetching articles from {feed_name} feed...")
        articles = fetch_rss_articles(feed_name, feed_url)

        if not articles:
            logger.warning(f"No articles found in {feed_name} RSS feed.")
            continue

        save_to_mongo(articles)

    logger.info("RSS scraper for Thanh Niên completed.")

if __name__ == "__main__":
    rss_thanhnien()
