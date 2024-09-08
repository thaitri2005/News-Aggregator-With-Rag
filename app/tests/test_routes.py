import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_testing import TestCase
import json
import sys
from bson import ObjectId
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

# Mock the loading of the environment variables
import os
os.environ['GEMINI_API_KEY'] = 'dummy_key'

# Import the Flask app and routes from the api module
from api.routes import api

class TestFlaskRoutes(TestCase):

    def create_app(self):
        # Create a Flask app instance for testing
        app = Flask(__name__)
        app.register_blueprint(api, url_prefix='/api')
        return app

    @patch('api.routes.articles_collection')
    def test_get_articles(self, mock_collection):
        # Mock the database call to return a list of articles
        mock_collection.find.return_value = [
            {"_id": ObjectId(), "title": "Test Article", "content": "Some content", "date": "2024-09-07", "source_url": "http://example.com"}
        ]

        # Send a GET request to the /api/articles endpoint
        response = self.client.get('/api/articles')

        # Assert the response status code and data
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Article', response.get_data(as_text=True))

    @patch('api.routes.articles_collection')
    def test_get_article(self, mock_collection):
        # Mock the database call to return a specific article
        mock_collection.find_one.return_value = {
            "_id": ObjectId("64edc1e8a9a7f72b8d91c9f3"),  # Use a valid ObjectId
            "title": "Test Article", "content": "Some content", "date": "2024-09-07", "source_url": "http://example.com"
        }

        # Send a GET request to the /api/articles/<valid_object_id> endpoint
        response = self.client.get('/api/articles/64edc1e8a9a7f72b8d91c9f3')

        # Assert the response status code and data
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Article', response.get_data(as_text=True))

    @patch('api.routes.articles_collection')
    def test_get_article_not_found(self, mock_collection):
        # Mock the database call to return None (article not found)
        mock_collection.find_one.return_value = None

        # Send a GET request to the /api/articles/<valid_object_id> endpoint
        response = self.client.get('/api/articles/64edc1e8a9a7f72b8d91c9f3')

        # Assert the response status code and data
        self.assertEqual(response.status_code, 404)
        self.assertIn('Article not found', response.get_data(as_text=True))

    @patch('api.routes.articles_collection')
    def test_add_article(self, mock_collection):
        # Send a POST request to the /api/articles endpoint with new article data
        response = self.client.post('/api/articles', data=json.dumps({
            "title": "New Article", "content": "New content", "date": "2024-09-07", "source_url": "http://example.com"
        }), content_type='application/json')

        # Assert the response status code and data
        self.assertEqual(response.status_code, 201)
        self.assertIn('Article added successfully', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
