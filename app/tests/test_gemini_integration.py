import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

# Mock the loading of the environment variables
os.environ['GEMINI_API_KEY'] = 'dummy_key'

from api.gemini_integration import summarize_article

class TestGeminiIntegration(unittest.TestCase):

    @patch('api.gemini_integration.genai.GenerativeModel')
    def test_summarize_article_success(self, mock_gen_model):
        # Mock the GenerativeModel instance
        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a summary."

        # Set up the chain of method calls
        mock_chat_session.send_message.return_value = mock_response
        mock_model_instance.start_chat.return_value = mock_chat_session
        mock_gen_model.return_value = mock_model_instance

        # Call the function to test
        result = summarize_article("This is an article.")

        # Assert the result
        self.assertEqual(result, "This is a summary.")

    @patch('api.gemini_integration.genai.GenerativeModel')
    def test_summarize_article_exception(self, mock_gen_model):
        # Mock the GenerativeModel instance to raise an exception
        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_chat_session.send_message.side_effect = Exception("API Error")
        mock_model_instance.start_chat.return_value = mock_chat_session
        mock_gen_model.return_value = mock_model_instance

        # Call the function to test
        result = summarize_article("This is an article.")

        # Assert the result
        self.assertEqual(result, "An error occurred while processing your request.")

if __name__ == '__main__':
    unittest.main()
