#app/api/scrapers/vnexpress_scraper.py
import requests
from bs4 import BeautifulSoup
import logging
from services.article_processor import ArticleProcessor  # Import ArticleProcessor
from models.article_model import Article
from utils.scraper_helpers import fetch_article_content_and_date, extract_article_links

logger = logging.getLogger(__name__)

# Initialize ArticleProcessor
article_processor = ArticleProcessor()

def scrape_vnexpress():
    """
    Scrape VNExpress articles from the homepage and process them for vectorization.
    """
    base_url = "https://vnexpress.net/"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract links and titles
        articles = extract_article_links(soup, "article.item-news h3.title-news a", base_url)

        if not articles:
            logger.warning("No articles found on VNExpress homepage.")
            return

        new_articles = []
        for article in articles:
            link = article['link']

            # Skip video articles based on URL
            if "video" in link:
                logger.info(f"Skipping video article: {link}")
                continue

            title = article['title']
            content, article_date = fetch_article_content_and_date(link, "article.fck_detail p.Normal")

            if content:
                article_obj = Article(
                    title=title,
                    content=content,
                    source_url=link,
                    date=article_date,
                    source="VNExpress"
                )
                new_articles.append(article_obj.to_dict())

        if new_articles:
            # Process and store articles in vector database
            for article in new_articles:
                try:
                    article_processor.process_and_store_article(article)
                    logger.info(f"Processed and stored article '{article['title']}' in vector DB.")
                except Exception as e:
                    logger.error(f"Failed to process article '{article['title']}': {e}")
        else:
            logger.warning("No valid articles to process from VNExpress.")

    except Exception as e:
        logger.error(f"Error while scraping VNExpress: {e}")

if __name__ == "__main__":
    scrape_vnexpress()
