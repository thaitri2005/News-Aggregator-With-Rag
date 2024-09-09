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
def summarize_article(article_text):
    # Update generation config for concise and optimized output
    generation_config = {
        "temperature": 0.7,  # Lowered for more focused output
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 512,  # Reduced token limit for summaries
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

    except Exception as e:
        logger.error(f"An error occurred during article summarization: {str(e)}")

        # Handle quota exhaustion or rate limits
        if '429' in str(e):
            return "Quota exhausted, summary not available."
        
        return "An error occurred while processing the article summary."
