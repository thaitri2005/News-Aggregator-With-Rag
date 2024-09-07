import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust the path for the test to find the 'api' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

from api.techcrunch_scraper import scrape_techcrunch, scrape_article_content

class TestTechCrunchScraper(unittest.TestCase):

    @patch('api.techcrunch_scraper.get_mongo_collection')  # Mock the Mongo collection function
    @patch('api.techcrunch_scraper.requests.get')
    def test_scrape_techcrunch(self, mock_get, mock_get_mongo_collection):
        # Mock the MongoDB collection
        mock_collection = MagicMock()
        mock_get_mongo_collection.return_value = mock_collection

        # Ensure find_one returns None to simulate no duplicate
        mock_collection.find_one.return_value = None

        # Mocking the response for the TechCrunch homepage
        mock_homepage_html = """
        <html>
            <article>
                <h2><a href="/test-article">Test Article</a></h2>
            </article>
        </html>
        """
        mock_article_html = """
        <html>
            <div class="entry-content wp-block-post-content is-layout-flow wp-block-post-content-is-layout-flow">
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

        mock_get.side_effect = [mock_response_homepage, mock_response_article]

        # Run the scraper function
        scrape_techcrunch()

        # Assert the correct URLs were called
        mock_get.assert_any_call("https://techcrunch.com", timeout=10)
        mock_get.assert_any_call("https://techcrunch.com/test-article", timeout=10)

        # Assert that insert_many was called (i.e., an article was inserted)
        self.assertTrue(mock_collection.insert_many.called)
        inserted_data = mock_collection.insert_many.call_args[0][0][0]
        self.assertEqual(inserted_data['title'], 'Test Article')
        self.assertEqual(inserted_data['source_url'], 'https://techcrunch.com/test-article')

    @patch('api.techcrunch_scraper.requests.get')
    def test_scrape_article_content(self, mock_get):
        mock_html = """
        <html>
            <div class="entry-content wp-block-post-content is-layout-flow wp-block-post-content-is-layout-flow">
                <p>This is the content of the test article.</p>
            </div>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = scrape_article_content("https://techcrunch.com/test-article")

        self.assertIn("This is the content of the test article.", content)
        mock_get.assert_called_once_with("https://techcrunch.com/test-article", timeout=10)

if __name__ == '__main__':
    unittest.main()
