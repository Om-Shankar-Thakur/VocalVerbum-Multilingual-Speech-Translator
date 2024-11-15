from record import record_audio
from transcribe import transcribe_audio
from lang_detect import detect_language
from translate import translate_text
from tts import text_to_speech

if __name__ == "__main__":
    audio_file = record_audio()

    transcription = transcribe_audio(audio_file)

    if transcription and transcription.strip():
        detected_lang = detect_language(transcription)

        translations = translate_text(transcription, detected_lang)

        print(f"Original Transcription: {transcription} in {detected_lang}")
        text_to_speech(transcription, lang=detected_lang)

        for lang, translation in translations.items():
            if translation:
                print(f"Translation in {lang}: {translation}")
                text_to_speech(translation, lang=lang)
            else:
                print(f"No valid translation available in {lang}")
    else:
        print("No valid transcription to process.")
