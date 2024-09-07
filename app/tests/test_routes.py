import unittest
from app import app

class TestRoutes(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
    
    def test_get_articles(self):
        response = self.app.get('/api/articles')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('articles' in response.json)
