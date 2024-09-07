import unittest
from unittest.mock import patch
from api.gemini_integration import summarize_article

class TestGeminiIntegration(unittest.TestCase):

    @patch('gemini_integration.genai.GenerativeModel')
    def test_summarize_article_success(self, mock_model):
        mock_model.return_value.start_chat.return_value.send_message.return_value.text = "Summarized content"
        result = summarize_article("Some article text")
        self.assertEqual(result, "Summarized content")
