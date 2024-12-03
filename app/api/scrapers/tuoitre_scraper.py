#app/api/scrapers/tuoitre_scraper.py
import logging
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import requests
from services.article_processor import ArticleProcessor  # Import ArticleProcessor
from models.article_model import Article
from utils.scraper_helpers import fetch_article_content_and_date, clean_html

logger = logging.getLogger(__name__)

# Initialize the ArticleProcessor
article_processor = ArticleProcessor()

# Define RSS Feeds for Tuổi Trẻ
RSS_FEEDS = {
    "Trang Chủ": "https://tuoitre.vn/rss/trang-chu.rss",
    "Tin Mới Nhất": "https://tuoitre.vn/rss/tin-moi-nhat.rss",
    "Thời Sự": "https://tuoitre.vn/rss/thoi-su.rss",
    "Thế Giới": "https://tuoitre.vn/rss/the-gioi.rss",
    "Pháp Luật": "https://tuoitre.vn/rss/phap-luat.rss",
    "Kinh Doanh": "https://tuoitre.vn/rss/kinh-doanh.rss",
    "Công Nghệ": "https://tuoitre.vn/rss/cong-nghe.rss",
    "Xe": "https://tuoitre.vn/rss/xe.rss",
    "Nhịp Sống Trẻ": "https://tuoitre.vn/rss/nhip-song-tre.rss",
    "Văn Hóa": "https://tuoitre.vn/rss/van-hoa.rss",
    "Giải Trí": "https://tuoitre.vn/rss/giai-tri.rss",
    "Thể Thao": "https://tuoitre.vn/rss/the-thao.rss",
    "Giáo Dục": "https://tuoitre.vn/rss/giao-duc.rss",
    "Khoa Học": "https://tuoitre.vn/rss/khoa-hoc.rss",
    "Sức Khỏe": "https://tuoitre.vn/rss/suc-khoe.rss",
    "Giả Thật": "https://tuoitre.vn/rss/gia-that.rss",
    "Thư Giãn": "https://tuoitre.vn/rss/thu-gian.rss",
    "Bạn Đọc": "https://tuoitre.vn/rss/ban-doc.rss",
    "Du Lịch": "https://tuoitre.vn/rss/du-lich.rss"
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
                    source=f"Tuổi Trẻ",
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
    Scrape Tuổi Trẻ articles using RSS feeds and store them in the vector database.
    """
    logger.info("Starting Tuổi Trẻ RSS scraper...")
    total_articles = 0

    for feed_name, feed_url in RSS_FEEDS.items():
        logger.info(f"Fetching articles from {feed_name} RSS feed...")
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
            logger.warning(f"No articles found in {feed_name} RSS feed.")

    if total_articles:
        logger.info(f"Total {total_articles} articles processed and stored from Tuổi Trẻ feeds.")
    else:
        logger.info("No valid articles found to process from Tuổi Trẻ feeds.")

if __name__ == "__main__":
    scrape_tuoitre()
