import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.newsdb
collection = db.articles

def scrape_techcrunch():
    url = "https://techcrunch.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('article')

    client = MongoClient('localhost', 27017)
    db = client['newsdb']
    collection = db['articles']

    for article in articles:
        title_tag = article.find('h2')
        if title_tag:
            title = title_tag.get_text(strip=True)
            content_tag = article.find('div', class_='post-block__content')
            content = content_tag.get_text(strip=True) if content_tag else "Content not found"
            link_tag = article.find('a', href=True)
            link = link_tag['href'] if link_tag else "Link not found"

            # Insert the article into the database
            article_data = {
                'title': title,
                'content': content,
                'url': link,
                'source': 'TechCrunch'
            }
            collection.insert_one(article_data)
            print(f"Inserted article: {title}")


if __name__ == "__main__":
    scrape_techcrunch()
