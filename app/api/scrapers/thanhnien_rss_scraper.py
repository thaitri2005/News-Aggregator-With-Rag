# app/api/scrapers/thanhnien_rss_scraper.py
import feedparser
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from services.mongo_service import save_articles
from models.article_model import Article
from utils.scraper_helpers import clean_html

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "Trang Chủ": "https://thanhnien.vn/rss/home.rss"
}

def scrape_article_content(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        sapo = soup.find('h2', class_='detail-sapo')
        sapo_text = sapo.get_text(strip=True) if sapo else ''

        content_div = soup.find('div', class_='detail-content.afcbc-body')
        content = "\n".join([p.get_text(strip=True) for p in content_div.find_all('p')]) if content_div else ''
        
        full_content = f"{sapo_text}\n\n{content}"
        return full_content
    except Exception as e:
        logger.error(f"Error scraping article content from {article_url}: {e}")
        return None

def fetch_rss_articles(feed_name, feed_url):
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
    logger.info("Starting Thanh Niên RSS scraper...")
    for feed_name, feed_url in RSS_FEEDS.items():
        logger.info(f"Fetching articles from {feed_name} feed...")
        articles = fetch_rss_articles(feed_name, feed_url)
        if articles:
            save_articles('articles', articles)
        else:
            logger.warning(f"No articles found in {feed_name} feed.")
    logger.info("Thanh Niên RSS scraper completed.")

if __name__ == "__main__":
    scrape_thanhnien_rss()