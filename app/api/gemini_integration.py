# app/api/gemini_integration.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import logging
import time

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

# Summarize article function in Vietnamese
def summarize_article(article_text, max_retries=3):
    """
    Summarizes an article using the Gemini API in Vietnamese.

    Parameters:
        article_text (str): The text of the article to be summarized.
        max_retries (int): The maximum number of retries in case of failures.

    Returns:
        str: The summarized text or an appropriate error message.
    """

    # Update generation config for optimized output
    generation_config = {
        "temperature": 0.5,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 512,
        "response_mime_type": "text/plain",
    }

    # Define the model configuration
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  # Using "flash" to accommodate higher quota
        generation_config=generation_config,
    )

    # Ensure prompt is clear and precise, with instructions to summarize in Vietnamese
    prompt = (
        "Tóm tắt bài báo sau bằng tiếng Việt trong vòng 5 câu trở xuống. "
        "Hãy tóm gọn và chỉ cung cấp tóm tắt mà không thêm thông tin hoặc ngữ cảnh phụ."
    )

    # Retry logic in case of transient errors
    for attempt in range(max_retries):
        try:
            chat_session = model.start_chat(history=[])
            # Send the prompt along with the article text for summarization in Vietnamese
            response = chat_session.send_message(f"{prompt}\n\n{article_text}")
            summary = response.text.strip()

            # Ensure no extra language is included
            if not summary.startswith("Tóm tắt:"):
                return summary

            # Clean up if extra framing language is detected
            return summary.replace("Tóm tắt:", "").strip()

        except google_exceptions.ResourceExhausted as e:
            # Handle quota exhaustion error
            logger.error(f"Quota exhausted: {str(e)}")
            return "Quota exhausted, summary not available."

        except google_exceptions.InternalServerError as e:
            # Log the internal server error
            logger.error(f"Internal server error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff before retrying
            else:
                return "An internal server error occurred. Please try again later."

        except google_exceptions.GoogleAPICallError as e:
            # Log generic API call error
            logger.error(f"API call error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return "An API call error occurred. Please try again later."

        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error during article summarization (Attempt {attempt + 1}/{max_retries}).")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return "An unexpected error occurred while processing the article summary."

    # If retries are exhausted and the function hasn't returned, log the failure
    logger.error("Failed to summarize the article after multiple attempts.")
    return "Failed to summarize the article after multiple attempts."
