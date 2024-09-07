import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
import sys
import os

# Adjust the path for the test to find the 'api' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

# Import the functions from rag_model.py
from api.rag_model import convert_objectid_to_str, create_text_index, retrieve_articles

class TestRagModel(unittest.TestCase):

    def test_convert_objectid_to_str(self):
        # Test when the document contains ObjectId
        doc_with_objectid = {"_id": ObjectId("507f191e810c19729de860ea"), "name": "Test"}
        result = convert_objectid_to_str(doc_with_objectid)
        self.assertEqual(result["_id"], "507f191e810c19729de860ea")
        self.assertEqual(result["name"], "Test")

        # Test when the document does not contain ObjectId
        doc_without_objectid = {"name": "Test"}
        result = convert_objectid_to_str(doc_without_objectid)
        self.assertEqual(result["name"], "Test")

    @patch('api.rag_model.db.get_collection')
    def test_create_text_index(self, mock_get_collection):
        # Mock the articles_collection
        mock_articles_collection = MagicMock()
        mock_get_collection.return_value = mock_articles_collection

        # Call the function
        create_text_index()

        # Assert that the create_index method was called with the correct arguments
        mock_articles_collection.create_index.assert_called_once_with([("title", "text"), ("content", "text")])

    @patch('api.rag_model.db.get_collection')
    def test_retrieve_articles(self, mock_get_collection):
        # Mock the articles_collection and the search results
        mock_articles_collection = MagicMock()
        mock_get_collection.return_value = mock_articles_collection
        mock_search_results = [
            {"_id": ObjectId("507f191e810c19729de860ea"), "title": "Test Article 1"},
            {"_id": ObjectId("507f191e810c19729de860eb"), "title": "Test Article 2"}
        ]
        mock_articles_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_search_results

        # Call the function
        query = "test"
        page = 1
        limit = 5
        result = retrieve_articles(query, page, limit)

        # Check that the results were properly converted to strings
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["_id"], "507f191e810c19729de860ea")
        self.assertEqual(result[1]["_id"], "507f191e810c19729de860eb")
        self.assertEqual(result[0]["title"], "Test Article 1")
        self.assertEqual(result[1]["title"], "Test Article 2")

        # Assert that the find method was called with the correct query and pagination
        mock_articles_collection.find.assert_called_once_with(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        )
        mock_articles_collection.find.return_value.sort.assert_called_once_with([("score", {"$meta": "textScore"})])

if __name__ == '__main__':
    unittest.main()
