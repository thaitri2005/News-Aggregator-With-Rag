# app/api/scrapers/vnexpress_scraper.py
import requests
from bs4 import BeautifulSoup
import logging
from services.mongo_service import save_articles
from models.article_model import Article
from utils.scraper_helpers import fetch_article_content_and_date, extract_article_links

logger = logging.getLogger(__name__)

def scrape_vnexpress():
    base_url = "https://vnexpress.net/"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract links and titles
    articles = extract_article_links(soup, "article.item-news h3.title-news a", base_url)

    new_articles = []
    for article in articles:
        link = article['link']

        # Exclude video articles based on URL
        if "video" in link:
            logger.info(f"Skipping video article: {link}")
            continue

        title = article['title']
        content, article_date = fetch_article_content_and_date(link, "article.fck_detail p.Normal")
        
        if content:
            article = Article(
                title=title,
                content=content,
                source_url=link,
                date=article_date,
                source='VNExpress'
            )
            new_articles.append(article.to_dict())

    save_articles('articles', new_articles)

if __name__ == "__main__":
    scrape_vnexpress()
