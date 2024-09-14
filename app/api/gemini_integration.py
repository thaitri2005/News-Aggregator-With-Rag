# app/api/gemini_integration.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import logging

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

def summarize_article(article_text):
    # Update generation config for concise and optimized output
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 512,
        "response_mime_type": "text/plain",
    }

    # Define the model configuration
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    # Ensure prompt is clear and precise
    prompt = (
        "Summarize the following article in 5 sentences or less. "
        "Keep it concise and in natural language. "
        "Only provide the summary without any extra information or framing."
    )

    try:
        # Send the prompt along with the article text for summarization
        response = chat_session.send_message(f"{prompt}\n\n{article_text}")
        summary = response.text.strip()

        # Ensure no extra language is included
        if not summary.startswith("Summary:"):
            return summary

        # In case extra framing language is detected, clean up
        return summary.replace("Summary:", "").strip()

    except google_exceptions.ResourceExhausted as e:
        logger.error(f"Quota exhausted: {str(e)}")
        return "Quota exhausted, summary not available."
    except google_exceptions.InternalServerError as e:
        logger.error(f"Internal server error: {str(e)}")
        return "An internal error occurred while processing the article summary."
    except google_exceptions.GoogleAPICallError as e:
        logger.error(f"API call error: {str(e)}")
        return "An error occurred while processing the article summary."
    except Exception as e:
        logger.exception("Unexpected error during article summarization.")
        return "An unexpected error occurred while processing the article summary."
