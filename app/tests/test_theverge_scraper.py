import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Adjust the path for the test to find the 'api' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

# Import the scrape_theverge and fetch_article_content from the correct module
from api.theverge_scraper import scrape_theverge, fetch_article_content

class TestTheVergeScraper(unittest.TestCase):

    @patch('api.theverge_scraper.collection')
    @patch('api.theverge_scraper.requests.get')
    def test_scrape_theverge(self, mock_get, mock_collection):
        # Mocking the response for The Verge homepage
        mock_homepage_html = """
        <html>
            <a class="text-black hover:text-blurple" href="/test-article">Test Article</a>
        </html>
        """
        mock_article_html = """
        <html>
            <div class="duet--article--article-body-component-container">
                <p>This is the content of the test article.</p>
            </div>
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
        scrape_theverge()

        # Assert the first call was to The Verge homepage
        mock_get.assert_any_call("https://www.theverge.com", timeout=10)

        # Assert the second call was to the article URL
        mock_get.assert_any_call("https://www.theverge.com/test-article", timeout=10)

        # Check that the article was inserted into the database
        self.assertTrue(mock_collection.insert_many.called)
        inserted_data = mock_collection.insert_many.call_args[0][0][0]
        self.assertEqual(inserted_data['title'], 'Test Article')
        self.assertEqual(inserted_data['source_url'], 'https://www.theverge.com/test-article')

    @patch('api.theverge_scraper.requests.get')
    def test_fetch_article_content(self, mock_get):
        # Mocking the response for article content
        mock_html = """
        <html>
            <div class="duet--article--article-body-component-container">
                <p>This is the content of the test article.</p>
            </div>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = fetch_article_content("https://www.theverge.com/test-article")

        self.assertIn("This is the content of the test article.", content)
        mock_get.assert_called_once_with("https://www.theverge.com/test-article", timeout=10)

if __name__ == '__main__':
    unittest.main()