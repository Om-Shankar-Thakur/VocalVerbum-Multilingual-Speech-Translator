from record import record_audio
from transcribe import transcribe_audio
from lang_detect import detect_language
from translate import translate_text
from tts import text_to_speech

if __name__ == "__main__":
    # Record 10 seconds of audio
    audio_file = record_audio()

    # Transcribe the recorded audio
    transcription = transcribe_audio(audio_file)

    # Ensure transcription is valid
    if transcription and transcription.strip():
        # Detect language based on the transcription
        detected_lang = detect_language(transcription)

        # Translate text into multiple languages
        translations = translate_text(transcription, detected_lang)

        # Convert original transcription to speech in detected language
        print(f"Original Transcription: {transcription} in {detected_lang}")
        text_to_speech(transcription, lang=detected_lang)

        # Output and voice each translation
        for lang, translation in translations.items():
            if translation:
                print(f"Translation in {lang}: {translation}")
                # Convert translation to speech
                text_to_speech(translation, lang=lang)
            else:
                print(f"No valid translation available in {lang}")
    else:
        print("No valid transcription to process.")
