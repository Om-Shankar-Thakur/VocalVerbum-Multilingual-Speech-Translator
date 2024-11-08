import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
API_URL = os.getenv('API_URL')


def translate_text(text, src_lang='en', tgt_langs=None):
    """Translate the transcribed text into multiple target languages."""
    if tgt_langs is None:
        tgt_langs = ['es', 'fr', 'de', 'it', 'ru', 'zh', 'ar', 'hi']  # Default target languages

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    translations = {}
    for tgt_lang in tgt_langs:
        print(f"Translating text to {tgt_lang}: {text}")
        model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'

        payload = {"inputs": text}
        max_retries = 5
        retry_delay = 15

        for attempt in range(max_retries):
            response = requests.post(
                f"{API_URL}{model_name}",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                # Check the format of the API response
                try:
                    translation = response.json()[0]['translation_text']
                    print(f"Translation to {tgt_lang}: {translation}")
                    translations[tgt_lang] = translation
                except (KeyError, IndexError):
                    # Handle unexpected response structure
                    print(f"Unexpected response format: {response.json()}")
                    translations[tgt_lang] = None
                break
            elif response.status_code == 503:
                print(f"Model loading for {tgt_lang}. Retrying in {
                      retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Failed to translate text to {tgt_lang}: {response.text}")
                translations[tgt_lang] = None
                break

    return translations
