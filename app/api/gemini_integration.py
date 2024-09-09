import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Load environment variables from the .env file
load_dotenv()

# Safely access the environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

# Configure Gemini API with the API key
genai.configure(api_key=api_key)

# Set up logging for errors and process information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to summarize an article using the Gemini API
# Summarize article with fallback for quota issues
def summarize_article(article_text):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[]
    )

    try:
        response = chat_session.send_message(article_text)
        return response.text
    except Exception as e:
        logger.error(f"An error occurred during article summarization: {str(e)}")
        # Return a fallback message in case of quota exhaustion or other errors
        if '429' in str(e):
            return "Quota exhausted, summary not available."
        return "An error occurred while processing the article summary."
