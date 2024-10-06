# app/api/scrapers/vietnamnet_rss_scraper.py
import feedparser
import logging
from datetime import datetime
from services.mongo_service import save_articles
from models.article_model import Article
from utils.scraper_helpers import clean_html, fetch_article_content_and_date

logger = logging.getLogger(__name__)

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
    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            published_date = entry.get("published", None)

            date_obj = None
            if published_date:
                try:
                    date_obj = datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError as e:
                    logger.error(f"RSS date parsing failed for {published_date}: {e}")

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
    logger.info("Starting VietnamNet RSS scraper...")
    for feed_name, feed_url in RSS_FEEDS.items():
        articles = fetch_rss_articles(feed_name, feed_url)
        if articles:
            save_articles('articles', articles)
        else:
            logger.warning(f"No articles found in {feed_name} feed.")
    logger.info("VietnamNet RSS scraper completed.")

if __name__ == "__main__":
    scrape_vietnamnet_rss()
