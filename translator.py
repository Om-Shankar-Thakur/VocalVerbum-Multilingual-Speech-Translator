import os
import requests
import time
import sounddevice as sd
import numpy as np
import soundfile as sf
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
# from speechbrain.inference.vocoders import HIFIGAN
# from speechbrain.inference.TTS import Tacotron2
import whisper  # Using Whisper for transcription
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io

# Load environment variables from .env
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
API_URL = os.getenv('API_URL')

if not API_TOKEN or not API_URL:
    raise ValueError("API_TOKEN or API_URL is missing from the environment variables!")

# Ensure reproducible results
DetectorFactory.seed = 0

# # Load SpeechBrain TTS models (Tacotron2 + Hifi-GAN for speech synthesis)
# try:
#     tacotron2 = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech",
#                                        savedir="pretrained_models/tacotron2")
#     hifi_gan = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="pretrained_models/hifigan")
# except Exception as e:
#     print(f"Error loading models: {e}")
#     exit(1)


def detect_language(text):
    """Detect the language of the transcribed text."""
    try:
        lang = detect(text)
        print(f"Detected language: {lang}")
        supported_langs = ['en', 'es', 'fr', 'de', 'it', 'ru', 'zh', 'ar', 'hi']
        if lang not in supported_langs:
            print(f"Language '{lang}' is not supported for translation. Defaulting to English (en).")
            lang = 'en'  # Default to English if the detected language is unsupported
        return lang
    except Exception as e:
        print(f"Error detecting language: {e}")
        return 'en'  # Fallback to English


def translate_text(text, src_lang='en', tgt_langs=None):
    """Translate the transcribed text into multiple target languages."""
    if tgt_langs is None:
        tgt_langs = ['es', 'fr', 'de', 'it', 'ru', 'zh', 'ar', 'hi']  # Target languages

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    translations = {}
    for tgt_lang in tgt_langs:
        print(f"Translating text to {tgt_lang}: {text}")
        model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'

        # Skip unsupported translation models
        try:
            response = requests.get(f"https://huggingface.co/{model_name}")
            if response.status_code != 200:
                print(f"Model {model_name} not available, skipping translation to {tgt_lang}.")
                translations[tgt_lang] = None
                continue
        except Exception as e:
            print(f"Error checking model availability: {e}")
            translations[tgt_lang] = None
            continue

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
                translation = response.json()[0]['translation_text']
                print(f"Translation to {tgt_lang}: {translation}")
                translations[tgt_lang] = translation
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


def text_to_speech(text):
    tts = gTTS(text=text, lang='en')

    # Use BytesIO to avoid saving the file
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    # Load the audio into AudioSegment
    audio_segment = AudioSegment.from_mp3(audio_bytes)

    # Play the audio
    play(audio_segment)


def record_audio(duration=10, folder="audio", filename="input.wav"):
    """Record audio from the microphone for a set duration."""
    # Ensure the audio folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, filename)
    print(f"Recording audio for {duration} seconds...")
    samplerate = 16000  # Sample rate for audio recording
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()  # Wait for the recording to finish
    sf.write(filepath, recording, samplerate)
    print(f"Audio recording saved to {filepath}")
    return filepath


def transcribe_audio(audio_file):
    """Transcribe audio using Whisper model."""
    # Load the smaller Whisper model
    model = whisper.load_model("base")  # or "small", "medium"
    result = model.transcribe(audio_file)
    transcription = result['text']
    print(f"Transcription: {transcription}")
    return transcription


if __name__ == "__main__":
    # Record 10 seconds of audio
    audio_file = record_audio()

    # Transcribe the recorded audio
    transcription = transcribe_audio(audio_file)

    # Detect language based on the transcription
    detected_lang = detect_language(transcription)

    # Translate text into multiple languages
    translations = translate_text(transcription, detected_lang, tgt_langs=[
                                  'es', 'fr', 'de', 'it', 'ru', 'zh', 'ar', 'hi'])

    # Convert original transcription to speech
    text_to_speech(transcription)

    # Output translations
    for lang, translation in translations.items():
        print(f"Translation in {lang}: {translation}")
