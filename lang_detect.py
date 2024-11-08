from langdetect import detect, DetectorFactory

# Set seed for reproducible language detection
DetectorFactory.seed = 0


def detect_language(text):
    """Detect the language of the transcribed text."""
    try:
        lang = detect(text)
        print(f"Detected language: {lang}")
        return lang
    except Exception as e:
        print(f"Error detecting language: {e}")
        return 'en'  # Default to English in case of error
