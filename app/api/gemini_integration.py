# app/api/gemini_integration.py
import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import logging
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Safely access the environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

# Configure Gemini API with the API key
genai.configure(api_key=api_key)

def summarize_article(article_text, max_retries=3):
    """
    Summarizes an article using the Gemini API in Vietnamese.

    Parameters:
        article_text (str): The text of the article to be summarized.
        max_retries (int): The maximum number of retries in case of failures.

    Returns:
        str: The summarized text or an appropriate error message.
    """
    # Configuration for the generation process
    generation_config = {
        "temperature": 0.5,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 512,
        "response_mime_type": "text/plain",
    }

    # Define the model to use for summarization
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config=generation_config,
    )

    # Vietnamese summarization prompt
    prompt = (
        "Tóm tắt bài báo sau bằng tiếng Việt, khách quan và ngắn gọn trong không quá 4 câu. Chỉ tập trung vào các sự kiện chính và thông tin nổi bật. Đảm bảo giọng văn nghiêm túc, chuẩn mực và không thêm suy đoán hoặc ý kiến cá nhân."
    )

    for attempt in range(max_retries):
        try:
            # Initialize chat session and send summarization request
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(f"{prompt}\n\n{article_text}")
            summary = response.text.strip()

            # Clean up response
            if not summary.startswith("Tóm tắt:"):
                return summary

            return summary.replace("Tóm tắt:", "").strip()

        # Centralized exception handling
        except (google_exceptions.ResourceExhausted, google_exceptions.InternalServerError,
                google_exceptions.GoogleAPICallError) as e:
            logger.error(f"API error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return f"An error occurred: {str(e)}. Please try again later."

        except Exception as e:
            logger.exception(f"Unexpected error during summarization (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return "An unexpected error occurred. Please try again later."

    logger.error("Failed to summarize the article after multiple attempts.")
    return "Failed to summarize the article after multiple attempts."
