# app/api/scrapers/dantri_rss_scraper.py
import feedparser
import logging
from datetime import datetime
from services.article_processor import ArticleProcessor
from models.article_model import Article
from utils.scraper_helpers import clean_html, fetch_article_content_and_date
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

# Initialize the ArticleProcessor
article_processor = ArticleProcessor()

# Define RSS Feeds for Dân Trí
# Define RSS Feeds for Dân Trí
RSS_FEEDS = {
    "Trang Chủ": "https://dantri.com.vn/rss/home.rss",
    "Sự Kiện": "https://dantri.com.vn/rss/su-kien.rss",
    "Xã Hội": "https://dantri.com.vn/rss/xa-hoi.rss",
    "Thế Giới": "https://dantri.com.vn/rss/the-gioi.rss",
    "Giá Vàng": "https://dantri.com.vn/rss/gia-vang.rss",
    "Đời Sống": "https://dantri.com.vn/rss/doi-song.rss",
    "Thể Thao": "https://dantri.com.vn/rss/the-thao.rss",
    "Lao Động - Việc Làm": "https://dantri.com.vn/rss/lao-dong-viec-lam.rss",
    "Giáo Dục": "https://dantri.com.vn/rss/giao-duc.rss",
    "Tấm Lòng Nhân Ái": "https://dantri.com.vn/rss/tam-long-nhan-ai.rss",
    "Kinh Doanh": "https://dantri.com.vn/rss/kinh-doanh.rss",
    "Bất Động Sản": "https://dantri.com.vn/rss/bat-dong-san.rss",
    "Giải Trí": "https://dantri.com.vn/rss/giai-tri.rss",
    "Du Lịch": "https://dantri.com.vn/rss/du-lich.rss",
    "Pháp Luật": "https://dantri.com.vn/rss/phap-luat.rss",
    "Sức Khỏe": "https://dantri.com.vn/rss/suc-khoe.rss",
    "Sức Mạnh Số": "https://dantri.com.vn/rss/suc-manh-so.rss",
    "Ô Tô - Xe Máy": "https://dantri.com.vn/rss/o-to-xe-may.rss",
    "Tình Yêu - Giới Tính": "https://dantri.com.vn/rss/tinh-yeu-gioi-tinh.rss",
    "Khoa Học - Công Nghệ": "https://dantri.com.vn/rss/khoa-hoc-cong-nghe.rss",
    "An Sinh": "https://dantri.com.vn/rss/an-sinh.rss",
    "Bạn Đọc": "https://dantri.com.vn/rss/ban-doc.rss",
    "Tâm Điểm": "https://dantri.com.vn/rss/tam-diem.rss",
    "Dmagazine": "https://dantri.com.vn/rss/dmagazine.rss",
    "Infographic": "https://dantri.com.vn/rss/infographic.rss",
    "DNews": "https://dantri.com.vn/rss/dnews.rss",
    "Tọa Đàm Trực Tuyến": "https://dantri.com.vn/rss/toa-dam-truc-tuyen.rss",
    "Xổ Số": "https://dantri.com.vn/rss/xo-so.rss",
}


# CSS Selectors for Dân Trí Content
CONTENT_SELECTORS = [
    "div.singular-content",  # Primary
    "div.e-magazine__body"   # Secondary fallback
]

def parse_vietnamese_date(date_string):
    """
    Parse Vietnamese date strings into Python datetime objects, supporting multiple formats.
    """
    date_formats = [
        "%d/%m/%Y - %H:%M",              # Format like '02/12/2024 - 11:44'
        "%d %b %Y %H:%M:%S %z",          # Format like '02 Dec 2024 07:00:06 +0700'
        "%a, %d %b %Y %H:%M:%S %z"       # Format like 'Mon, 02 Dec 2024 10:30:19 +0700'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue  # Try the next format
    
    logger.error(f"Failed to parse Vietnamese date '{date_string}', using current datetime.")
    return datetime.now()




def fetch_full_article_content(url):
    """
    Fetch the full article content by trying multiple selectors.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try each content selector
        for selector in CONTENT_SELECTORS:
            content_element = soup.select_one(selector)
            if content_element:
                return clean_html(content_element.get_text())

        logger.warning(f"No content found for {url} using selectors {CONTENT_SELECTORS}")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch content from {url}: {e}")
        return None

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
            date_obj = parse_vietnamese_date(published_date) if published_date else datetime.now()

            # Fetch content and date from the article page
            full_content = fetch_full_article_content(link)

            if full_content:
                article = Article(
                    title=title,
                    content=full_content,
                    source_url=link,
                    date=date_obj,
                    source=f"Dân Trí"
                )
                articles.append(article.to_dict())

        return articles
    except Exception as e:
        logger.exception(f"Failed to fetch articles from RSS feed {feed_name}: {e}")
        return []

def scrape_dantri_rss():
    """
    Scrape Dân Trí articles using RSS feeds and store them in the vector database.
    """
    logger.info("Starting Dân Trí RSS scraper...")
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
        logger.info(f"Total {total_articles} articles processed and stored from Dân Trí feeds.")
    else:
        logger.info("No valid articles found to process from Dân Trí feeds.")


if __name__ == "__main__":
    scrape_dantri_rss()
