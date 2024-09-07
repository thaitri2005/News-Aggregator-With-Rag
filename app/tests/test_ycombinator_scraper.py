import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add 'app' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

from api.ycombinator_scraper import scrape_ycombinator, fetch_article_content
from bs4 import BeautifulSoup

class TestYCombinatorScraper(unittest.TestCase):

    @patch('api.ycombinator_scraper.collection')
    @patch('api.ycombinator_scraper.requests.get')
    def test_scrape_ycombinator(self, mock_get, mock_collection):
        # Mocking the response for the YCombinator homepage
        mock_homepage_html = """
        <html>
            <tr class='athing'>
                <span class='titleline'>
                    <a href="https://example.com">Test Article</a>
                </span>
            </tr>
        </html>
        """
        mock_article_html = """
        <html>
            <h1>Test Article</h1>
            <time>2024-09-07</time>
            <p>This is the content of the article.</p>
        </html>
        """

        # Set up the mock responses for both homepage and article content
        mock_response_homepage = MagicMock()
        mock_response_homepage.status_code = 200
        mock_response_homepage.text = mock_homepage_html

        mock_response_article = MagicMock()
        mock_response_article.status_code = 200
        mock_response_article.text = mock_article_html

        # Set side_effect to return the appropriate response for each call
        mock_get.side_effect = [mock_response_homepage, mock_response_article]

        # Mock the MongoDB collection to avoid actual database interactions
        mock_collection.find_one.return_value = None
        mock_collection.insert_many.return_value = None

        # Call the function being tested
        scrape_ycombinator()

        # Assert the first call was to the YCombinator homepage
        mock_get.assert_any_call("https://news.ycombinator.com/", timeout=10)

        # Assert the second call was to the article URL
        mock_get.assert_any_call("https://example.com", headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}, timeout=10)

        # Check that the article was inserted into the database
        self.assertTrue(mock_collection.insert_many.called)
        inserted_data = mock_collection.insert_many.call_args[0][0][0]
        self.assertEqual(inserted_data['title'], 'Test Article')
        self.assertEqual(inserted_data['source_url'], 'https://example.com')

    @patch('api.ycombinator_scraper.requests.get')
    def test_fetch_article_content(self, mock_get):
        # Mocking the response for article content
        mock_html = """
        <html>
            <h1>Test Article</h1>
            <time>2024-09-07</time>
            <p>This is the content of the article.</p>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = fetch_article_content("https://example.com")

        self.assertIn("This is the content of the article.", content)
        mock_get.assert_called_once_with("https://example.com", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}, timeout=10)

if __name__ == '__main__':
    unittest.main()
