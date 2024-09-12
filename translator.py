import os
import requests
import time
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from speechbrain.pretrained import Tacotron2, HifiGan
import soundfile as sf

# Load environment variables from .env
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
API_URL = os.getenv('API_URL')

# Ensure reproducible results
DetectorFactory.seed = 0

# Load SpeechBrain TTS models (Tacotron2 + Hifi-GAN for speech synthesis)
tacotron2 = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech",
                                   savedir="pretrained_models/tacotron2-ljspeech")
hifi_gan = HifiGan.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="pretrained_models/hifigan-ljspeech")


def detect_language(text):
    """Detect the language of the transcribed text."""
    try:
        lang = detect(text)
        print(f"Detected language: {lang}")
        return lang
    except Exception as e:
        print(f"Error detecting language: {e}")
        return None


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
        payload = {
            "inputs": text
        }

        max_retries = 5
        retry_delay = 15

        for attempt in range(max_retries):
            response = requests.post(
                f"{API_URL}{model_name}",  # Fetching from .env
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                translation = response.json()[0]['translation_text']
                print(f"Translation to {tgt_lang}: {translation}")
                translations[tgt_lang] = translation
                break
            elif response.status_code == 503:
                print(
                    f"Model is loading for {tgt_lang}. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Failed to translate text to {tgt_lang}: {response.text}")
                translations[tgt_lang] = None
                break

    return translations


def text_to_speech(text, output_file="output.wav"):
    """Convert text to speech using Tacotron2 and HiFi-GAN models."""
    # Generate mel-spectrogram using Tacotron2
    mel_output, _ = tacotron2.encode_text(text)
    # Convert spectrogram to waveform using HiFi-GAN
    waveforms = hifi_gan.decode_batch(mel_output)
    waveform = waveforms.squeeze(1)
    # Save the speech to a file
    sf.write(output_file, waveform.cpu().numpy(), 22050)
    print(f"Speech saved to {output_file}")


# Example usage
if __name__ == "__main__":
    # Example transcription to translate and synthesize (You can pass in transcription from SST.py)
    transcription = "Hello, how are you today?"

    # Detect language
    detected_lang = detect_language(transcription)

    # Translate text into multiple languages
    translations = translate_text(transcription, detected_lang, tgt_langs=[
                                  'es', 'fr', 'de', 'it', 'ru', 'zh', 'ar', 'hi'])

    # Convert original transcription to speech
    text_to_speech(transcription, output_file="output_speech.wav")

    # Output translations
    for lang, translation in translations.items():
        print(f"Translation in {lang}: {translation}")
