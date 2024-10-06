# app/api/scrapers/tuoitre_scraper.py
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from services.mongo_service import save_articles
from models.article_model import Article
from utils.scraper_helpers import extract_article_links, fetch_article_content_and_date

logger = logging.getLogger(__name__)

def scrape_tuoitre():
    base_url = "https://tuoitre.vn"
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching Tuổi Trẻ page: {e}")
        return

    articles = extract_article_links(soup, 'div.box-category-item a.box-category-link-title', base_url)

    new_articles = []
    for article in articles:
        title = article['title']
        link = article['link']

        if any(exclusion in link for exclusion in ["video", "podcast", "cuoituan", "cuoi", "playlist"]):
            logger.info(f"Skipping article: {link}")
            continue

        full_content, article_date = fetch_article_content_and_date(link, "div.detail-content.afcbc-body")

        if full_content:
            article = Article(
                title=title,
                content=full_content,
                source_url=link,
                date=article_date or datetime.now(),
                source='Tuổi Trẻ'
            )
            new_articles.append(article.to_dict())

    if new_articles:
        save_articles('articles', new_articles)
    else:
        logger.info("No valid articles to save.")

if __name__ == "__main__":
    scrape_tuoitre()
