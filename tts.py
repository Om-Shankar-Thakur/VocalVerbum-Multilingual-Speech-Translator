from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io

# Mapping of target languages to `gTTS` language codes (not all languages are supported)
TTS_LANG_CODES = {
    'en': 'en',
    'es': 'es',
    'fr': 'fr',
    'de': 'de',
    'it': 'it',
    'ru': 'ru',
    'zh': 'zh-CN',
    'ar': 'ar',
    'hi': 'hi'
}


def text_to_speech(text, lang='en'):
    """Convert text to speech in a specified language."""
    if lang not in TTS_LANG_CODES:
        print(f"TTS not supported for language: {lang}. Defaulting to English.")
        lang = 'en'  # Default to English if the language is unsupported

    try:
        tts = gTTS(text=text, lang=TTS_LANG_CODES[lang])
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        audio_segment = AudioSegment.from_mp3(audio_bytes)
        play(audio_segment)
    except Exception as e:
        print(f"Error generating TTS for language {lang}: {e}")
