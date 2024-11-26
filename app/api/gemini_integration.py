# app/api/gemini_integration.py
import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import logging
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Safely access the API key from the environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

# Configure the Gemini API
try:
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully.")
except Exception as e:
    logger.exception("Failed to configure Gemini API.")
    raise

def summarize_article(article_text, max_retries=3, prompt=None):
    """
    Summarizes an article using the Gemini API.
    :param article_text: The full text of the article to summarize.
    :param max_retries: Number of retries in case of API errors.
    :param prompt: Custom prompt for summarization (optional).
    :return: Summarized text or an error message.
    """
    if not article_text or len(article_text.strip()) == 0:
        logger.warning("Empty or invalid article text provided.")
        return "No content to summarize."

    if prompt is None:
        # Default prompt for summarization
        prompt = (
            "Tóm tắt bài báo sau bằng tiếng Việt, khách quan và ngắn gọn trong không quá 4 câu. "
            "Chỉ tập trung vào các sự kiện chính và thông tin nổi bật. "
            "Đảm bảo giọng văn nghiêm túc, chuẩn mực và không thêm suy đoán hoặc ý kiến cá nhân."
        )

    generation_config = {
        "temperature": 0.5,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 512,
        "response_mime_type": "text/plain",
    }

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )
        logger.info("Gemini GenerativeModel initialized successfully.")
    except Exception as e:
        logger.exception("Failed to initialize Gemini GenerativeModel.")
        return "Failed to initialize Gemini API. Please check your configuration."

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}: Summarizing article with {len(article_text)} characters.")
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(f"{prompt}\n\n{article_text}")
            summary = response.text.strip()

            logger.info("Article summarized successfully.")
            return summary.replace("Tóm tắt:", "").strip()

        except (google_exceptions.ResourceExhausted, google_exceptions.InternalServerError,
                google_exceptions.GoogleAPICallError) as e:
            logger.error(f"Gemini API error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return f"API error: {str(e)}. Please try again later."

        except Exception as e:
            logger.exception(f"Unexpected error during summarization (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return "Unexpected error during summarization. Please try again later."

    logger.error("Failed to summarize the article after multiple attempts.")
    return "Failed to summarize the article after multiple attempts."
