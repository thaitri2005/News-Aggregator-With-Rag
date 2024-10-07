# app/utils/scraper_helpers.py
import html
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

def clean_html(html_content):
    """
    Cleans HTML content by removing tags and returning plain text.
    Also decodes any HTML entities like &apos; or &amp;.
    """
    # Check if the input looks like a file path or URL
    if isinstance(html_content, str) and (html_content.startswith(('http://', 'https://', '/', './', '../'))):
        logger.warning("Input resembles a file path or URL. Check the source of the HTML content.")
        return ""

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Get the text and decode HTML entities
    clean_text = soup.get_text(separator="\n").strip()
    clean_text = html.unescape(clean_text)  # Decode HTML entities like &apos;, &amp;

    return clean_text


def fetch_article_content_and_date(url, content_selector):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract article content
        article_content = soup.select_one(content_selector)
        if not article_content:
            raise ValueError(f"Content not found for {url}")
        
        content = article_content.get_text(separator="\n").strip()

        # Extract publication date
        pub_date_str = None
        pub_date = None
        
        date_selectors = [
            'div.publish-date',  
            'time', 
            'meta[property="article:published_time"]',
            'meta[name="pubdate"]', 'meta[name="og:pubdate"]',
        ]

        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                if date_element.name == 'meta':
                    pub_date_str = date_element.get('content')
                else:
                    pub_date_str = date_element.get_text(strip=True)
                if pub_date_str:
                    break
        
        # If no date found, log and return current datetime
        if not pub_date_str:
            logger.warning(f"Date not found for {url}, using current datetime.")
            pub_date = datetime.now()
        else:
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # RSS common format
                '%a, %d %b %y %H:%M:%S %z',
                '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601 format
                '%Y-%m-%dT%H:%M:%S.%fZ',     # ISO format with milliseconds
                '%d/%m/%Y %H:%M',            # VN format with time
                '%d-%m-%Y %H:%M',            # VN format with time
                '%d/%m/%Y',                  # VN format without time
                '%d-%m-%Y',                  # VN format without time
                '%d/%m/%Y  -  %H:%M'         # For format like '03/10/2024 - 09:10'
            ]
            for fmt in date_formats:
                try:
                    pub_date = datetime.strptime(pub_date_str.strip(), fmt)
                    break
                except ValueError:
                    continue
            else:
                logger.warning(f"Date parsing failed for {pub_date_str}, using current datetime.")
                pub_date = datetime.now()

        return content, pub_date

    except Exception as e:
        logger.error(f"Error fetching content for {url}: {e}")
        return None, None

def extract_article_links(soup, selector, base_url=None):
    """
    Extracts article links and titles from the given BeautifulSoup object.
    Optionally appends the base URL to relative links.
    """
    articles = []
    links = soup.select(selector)

    for link in links:
        title = link.get_text(strip=True)
        href = link.get('href')
        if base_url and href and not href.startswith('http'):
            href = base_url + href
        if href:
            articles.append({'title': title, 'link': href})

    return articles