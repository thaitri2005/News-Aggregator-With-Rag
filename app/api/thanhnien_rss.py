import feedparser
import logging
import requests
from pymongo.errors import PyMongoError
from datetime import datetime
from bs4 import BeautifulSoup
from tuoitre_scraper import get_mongo_collection  # Import the existing get_mongo_collection function

logger = logging.getLogger(__name__)

# List of RSS Feed URLs for Thanh Niên
RSS_FEEDS = {
    "Trang Chủ": "https://thanhnien.vn/rss/home.rss"
}

# Function to clean HTML content and remove unwanted tags
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

# Function to scrape the actual content from the article page
def scrape_article_content(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the headline summary (sapo)
        sapo = soup.find('h2', class_='detail-sapo')
        sapo_text = sapo.get_text(strip=True) if sapo else ''

        # Extract the main article content
        content_div = soup.find('div', class_='detail-content afcbc-body')
        if content_div:
            paragraphs = content_div.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        else:
            content = ''

        # Combine sapo and content
        full_content = f"{sapo_text}\n\n{content}"

        return full_content
    except Exception as e:
        logger.error(f"Error scraping article content from {article_url}: {e}")
        return None

# Function to fetch articles from a given RSS feed URL
def fetch_rss_articles(feed_name, feed_url):
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            published_date = entry.published
            summary = clean_html(entry.summary)
            image_url = extract_image(entry.summary)

            try:
                # Convert published_date to a datetime object
                date_obj = datetime.strptime(published_date, '%a, %d %b %y %H:%M:%S %z')
            except ValueError as e:
                logger.error(f"Date parsing failed for {published_date}: {e}")
                continue  # Skip this article if the date can't be parsed

            # Scrape article content from the article page
            full_content = scrape_article_content(link)

            if full_content:
                articles.append({
                    "title": title,
                    "content": full_content,
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
