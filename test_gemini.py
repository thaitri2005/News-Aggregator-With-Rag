#!/usr/bin/env python3
"""Minimal test for Gemini summarization."""

import os
import sys
from dotenv import load_dotenv

# Load .env from deployment folder
load_dotenv(os.path.join(os.path.dirname(__file__), 'deployment', '.env'))

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from api.gemini_integration import summarize_article

# Simple test text
test_text = """
Thái Lan cho phép bán bia rượu buổi chiều sau nhiều năm áp dụng lệnh cấm.
Chính phủ Thái Lan vừa quyết định nới lỏng quy định về bán rượu bia trong giờ nghỉ trưa.
Người dân và du khách giờ đây có thể mua đồ uống có cồn từ 11h đến 14h.
Đây là thay đổi lớn sau nhiều năm thực thi lệnh cấm nghiêm ngặt.
"""

print("=" * 60)
print("Testing Gemini summarization function...")
print("=" * 60)
print(f"\nInput text ({len(test_text)} chars):")
print(test_text)
print("\n" + "=" * 60)
print("Calling summarize_article()...")
print("=" * 60)

result = summarize_article(test_text)

print("\nResult:")
print(result)
print("\n" + "=" * 60)
print("DONE")
print("=" * 60)

