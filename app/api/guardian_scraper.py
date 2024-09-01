import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.newsdb
collection = db.articles

def scrape_guardian():
    url = 'https://www.theguardian.com/world'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('div', class_='fc-item__container')

    for article in articles:
        title = article.find('a').get_text(strip=True)
        link = article.find('a')['href']
        date = datetime.now()

        # Check for duplicate articles based on title
        if collection.find_one({'title': title}):
            continue

        content = fetch_article_content(link)
        if content:
            article_data = {
                'title': title,
                'content': content,
                'date': date,
                'source_url': link
            }
            collection.insert_one(article_data)
            print(f'Inserted article: {title}')

def fetch_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')

        content = ' '.join([para.get_text(strip=True) for para in paragraphs])
        return content
    except Exception as e:
        print(f'Error fetching content from {url}: {e}')
        return None

if __name__ == "__main__":
    scrape_guardian()
