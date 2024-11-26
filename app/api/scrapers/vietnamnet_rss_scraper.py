# app/api/scrapers/vietnamnet_rss_scraper.py
import feedparser
import logging
from datetime import datetime
from services.article_processor import ArticleProcessor  # Import ArticleProcessor
from models.article_model import Article
from utils.scraper_helpers import clean_html, fetch_article_content_and_date

logger = logging.getLogger(__name__)

# Initialize the ArticleProcessor
article_processor = ArticleProcessor()

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

def fetch_rss_articles(feed_name, feed_url):
    """
    Fetch articles from an RSS feed and process them for full content and date parsing.
    """
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            published_date = entry.get("published", None)

            # Parse publication date
            date_obj = None
            if published_date:
                try:
                    date_obj = datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError as e:
                    logger.error(f"RSS date parsing failed for {published_date}: {e}")

            # Fetch content and date from the article page
            full_content, article_date = fetch_article_content_and_date(link, "div.contentDetail__main-reading")
            final_date = article_date or date_obj or datetime.now()

            if full_content:
                article = Article(
                    title=title,
                    content=full_content,
                    source_url=link,
                    date=final_date,
                    source=f"VietnamNet - {feed_name}"
                )
                articles.append(article.to_dict())

        return articles
    except Exception as e:
        logger.exception(f"Failed to fetch articles from RSS feed {feed_name}: {e}")
        return []

def scrape_vietnamnet_rss():
    """
    Scrape VietnamNet articles using RSS feeds and store them in the vector database.
    """
    logger.info("Starting VietnamNet RSS scraper...")
    total_articles = 0

    for feed_name, feed_url in RSS_FEEDS.items():
        articles = fetch_rss_articles(feed_name, feed_url)

        if articles:
            for article in articles:
                try:
                    article_processor.process_and_store_article(article)
                    logger.info(f"Processed and stored article '{article['title']}' in vector DB.")
                except Exception as e:
                    logger.error(f"Failed to process article '{article['title']}': {e}")
            total_articles += len(articles)
        else:
            logger.warning(f"No articles found in {feed_name} feed.")

    if total_articles:
        logger.info(f"Total {total_articles} articles processed and stored from VietnamNet feeds.")
    else:
        logger.info("No valid articles found to process from VietnamNet feeds.")

if __name__ == "__main__":
    scrape_vietnamnet_rss()
