#app/api/scrapers/thanhnien_rss_scraper.py
import feedparser
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from services.article_processor import ArticleProcessor  # Import the ArticleProcessor
from models.article_model import Article
from utils.scraper_helpers import clean_html

logger = logging.getLogger(__name__)

# Initialize ArticleProcessor
article_processor = ArticleProcessor()

RSS_FEEDS = {
    "Trang Chủ": "https://thanhnien.vn/rss/home.rss"
}

def scrape_article_content(article_url):
    """
    Scrapes the full content of an article given its URL.
    """
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract article content
        sapo = soup.find('h2', class_='detail-sapo')
        sapo_text = sapo.get_text(strip=True) if sapo else ''

        content_div = soup.find('div', class_='detail-content.afcbc-body')
        content = "\n".join([p.get_text(strip=True) for p in content_div.find_all('p')]) if content_div else ''

        # Combine extracted content
        full_content = f"{sapo_text}\n\n{content}"
        return full_content
    except Exception as e:
        logger.error(f"Error scraping article content from {article_url}: {e}")
        return None

def fetch_rss_articles(feed_name, feed_url):
    """
    Fetches articles from an RSS feed and processes them into Article objects.
    """
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            published_date = entry.published

            try:
                date_obj = datetime.strptime(published_date, '%a, %d %b %y %H:%M:%S %z')
            except ValueError as e:
                logger.error(f"Date parsing failed for {published_date}: {e}")
                continue

            full_content = scrape_article_content(link)

            if full_content:
                article = Article(
                    title=title,
                    content=full_content,
                    source_url=link,
                    date=date_obj,
                    source=f"Thanh Niên - {feed_name}"
                )
                articles.append(article.to_dict())

        return articles
    except Exception as e:
        logger.exception(f"Failed to fetch articles from RSS feed {feed_name}: {e}")
        return []

def scrape_thanhnien_rss():
    """
    Main function for scraping Thanh Niên RSS feeds.
    - Processes articles for vectorization and stores them in the vector database.
    """
    logger.info("Starting Thanh Niên RSS scraper...")
    for feed_name, feed_url in RSS_FEEDS.items():
        logger.info(f"Fetching articles from {feed_name} feed...")
        articles = fetch_rss_articles(feed_name, feed_url)

        if articles:
            for article in articles:
                try:
                    article_processor.process_and_store_article(article)
                    logger.info(f"Processed and stored article '{article['title']}' in vector DB.")
                except Exception as e:
                    logger.error(f"Failed to process article '{article['title']}': {e}")
        else:
            logger.warning(f"No articles found in {feed_name} feed.")

    logger.info("Thanh Niên RSS scraper completed.")

if __name__ == "__main__":
    scrape_thanhnien_rss()
