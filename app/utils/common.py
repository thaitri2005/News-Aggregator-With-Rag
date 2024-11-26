#app/utils/common.py
import unicodedata
import re

def normalize_text(text):
    """
    Normalize Vietnamese text by removing diacritics, converting to lowercase, 
    and removing unnecessary punctuation. This improves search accuracy.
    """
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    sanitized_text = re.sub(r'[^\w\s]', '', normalized_text)
    return sanitized_text.strip()
