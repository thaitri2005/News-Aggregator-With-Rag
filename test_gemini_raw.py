#!/usr/bin/env python3
"""Direct Gemini API test without our wrapper."""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), 'deployment', '.env'))

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: No GEMINI_API_KEY found")
    exit(1)

genai.configure(api_key=api_key)

test_text = """
Thái Lan cho phép bán bia rượu buổi chiều sau nhiều năm áp dụng lệnh cấm.
Chính phủ Thái Lan vừa quyết định nới lỏng quy định về bán rượu bia trong giờ nghỉ trưa.
"""

prompt = "Tóm tắt ngắn gọn bài viết sau bằng tiếng Việt:"

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

print("=" * 60)
print("TEST 1: gemini-2.5-flash with BLOCK_NONE")
print("=" * 60)
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        safety_settings=safety_settings,
    )
    response = model.generate_content(f"{prompt}\n\n{test_text}")
    
    print(f"Finish reason: {response.candidates[0].finish_reason}")
    print(f"Safety ratings: {response.candidates[0].safety_ratings}")
    print(f"Text: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("TEST 2: gemini-1.5-flash with BLOCK_NONE")
print("=" * 60)
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        safety_settings=safety_settings,
    )
    response = model.generate_content(f"{prompt}\n\n{test_text}")
    
    print(f"Finish reason: {response.candidates[0].finish_reason}")
    print(f"Safety ratings: {response.candidates[0].safety_ratings}")
    print(f"Text: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("TEST 3: gemini-1.5-pro with BLOCK_NONE")
print("=" * 60)
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings=safety_settings,
    )
    response = model.generate_content(f"{prompt}\n\n{test_text}")
    
    print(f"Finish reason: {response.candidates[0].finish_reason}")
    print(f"Safety ratings: {response.candidates[0].safety_ratings}")
    print(f"Text: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("TEST 4: English text with gemini-2.5-flash")
print("=" * 60)
english_text = "Thailand allows afternoon alcohol sales after years of strict ban."
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        safety_settings=safety_settings,
    )
    response = model.generate_content(f"Summarize: {english_text}")
    
    print(f"Finish reason: {response.candidates[0].finish_reason}")
    print(f"Text: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
