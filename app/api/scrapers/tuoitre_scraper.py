# app/api/scrapers/tuoitre_scraper.py
import logging
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import requests
from services.mongo_service import save_articles
from services.article_processor import ArticleProcessor  # Import ArticleProcessor
from models.article_model import Article
from utils.scraper_helpers import fetch_article_content_and_date, clean_html

logger = logging.getLogger(__name__)

# Initialize the ArticleProcessor
article_processor = ArticleProcessor()

RSS_FEEDS = {
    "Tin Mới Nhất": "https://tuoitre.vn/rss/tin-moi-nhat.rss",
    "Thế Giới": "https://tuoitre.vn/rss/the-gioi.rss",
    "Thời Sự": "https://tuoitre.vn/rss/thoi-su.rss",
}

def fetch_rss_articles(feed_name, feed_url):
    """
    Fetch articles from an RSS feed and process each article for full content and date parsing.
    """
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            published_date = entry.get("published", None)

            # Attempt to parse the published date
            article_date = None
            if published_date:
                # Replace "GMT+7" with "+0700" for compatibility
                cleaned_date = published_date.replace("GMT+7", "+0700")
                date_formats = [
                    '%a, %d %b %Y %H:%M:%S %z',  # RSS common format with timezone
                ]
                for fmt in date_formats:
                    try:
                        article_date = datetime.strptime(cleaned_date.strip(), fmt)
                        break
                    except ValueError:
                        continue
                else:
                    logger.warning(f"Failed to parse date for {link}: {published_date}")

            logger.info(f"Processing article: Title: {title}, Link: {link}")

            # Fetch content from the article link
            full_content, content_date = fetch_article_content_and_date(link, "div.detail-content.afcbc-body")
            if not full_content or full_content.strip() == "":
                logger.warning(f"Skipping article with missing or empty content: {link}")
                continue

            # Use the publication date from RSS or fallback to the date extracted from the article
            final_date = content_date or article_date or datetime.now()

            if title and link and full_content:  # Ensure all essential fields are present
                article = Article(
                    title=title,
                    content=full_content,
                    source_url=link,
                    date=final_date,
                    source=f"Tuổi Trẻ - {feed_name}",
                )
                articles.append(article.to_dict())
            else:
                logger.warning(f"Skipping article due to missing essential fields: {link}")

        return articles
    except Exception as e:
        logger.error(f"Error fetching RSS feed {feed_name}: {e}")
        return []

def scrape_tuoitre():
    """
    Scrape Tuổi Trẻ articles using RSS feeds.
    """
    logger.info("Starting Tuổi Trẻ RSS scraper...")
    new_articles = []

    for feed_name, feed_url in RSS_FEEDS.items():
        logger.info(f"Fetching articles from {feed_name} RSS feed...")
        articles = fetch_rss_articles(feed_name, feed_url)
        if articles:
            new_articles.extend(articles)
            # Step 1: Save articles to MongoDB
            save_articles("articles", articles)
            logger.info(f"Saved {len(articles)} articles from {feed_name} to MongoDB.")

            # Step 2: Process and store articles in the vector database
            for article in articles:
                try:
                    article_processor.process_and_store_article(article)
                    logger.info(f"Processed and stored article '{article['title']}' in vector DB.")
                except Exception as e:
                    logger.error(f"Failed to process article '{article['title']}': {e}")
        else:
            logger.warning(f"No articles found in {feed_name} RSS feed.")

    if new_articles:
        logger.info(f"Total {len(new_articles)} articles saved and processed from Tuổi Trẻ feeds.")
    else:
        logger.info("No valid articles to save.")

if __name__ == "__main__":
    scrape_tuoitre()
