import streamlit as st
from record import record_audio
from transcribe import transcribe_audio
from lang_detect import detect_language
from translate import translate_text
from tts import text_to_speech

if "audio_file" not in st.session_state:
    st.session_state["audio_file"] = None
if "transcription" not in st.session_state:
    st.session_state["transcription"] = None
if "detected_lang" not in st.session_state:
    st.session_state["detected_lang"] = None
if "translations" not in st.session_state:
    st.session_state["translations"] = {}

st.title("VocalVerbum: Multilingual Speech Translator")
st.write("Record audio, transcribe, translate, and listen to translations.")

st.sidebar.title("Instructions")
st.sidebar.write("""
1. Click 'Record' to capture audio.
2. The app will transcribe, detect the language, translate, and provide audio playback.
""")

if st.button("Record Audio"):
    with st.spinner("Recording for 10 seconds..."):
        audio_file = record_audio(duration=10)
        st.success("Audio recorded successfully!")
        st.session_state["audio_file"] = audio_file  # Save audio file in session state
        st.session_state["transcription"] = None     # Reset transcription state
        st.session_state["detected_lang"] = None     # Reset detected language state
        st.session_state["translations"] = {}        # Reset translations state

if st.session_state["audio_file"]:
    st.audio(st.session_state["audio_file"], format="audio/wav")

    if st.session_state["transcription"] is None:
        transcription = transcribe_audio(st.session_state["audio_file"])
        if transcription:
            st.session_state["transcription"] = transcription
            st.subheader("Transcription")
            st.write(transcription)
        else:
            st.error("Failed to transcribe audio.")
    else:
        st.subheader("Transcription")
        st.write(st.session_state["transcription"])

    if st.session_state["transcription"] and st.session_state["detected_lang"] is None:
        detected_lang = detect_language(st.session_state["transcription"])
        st.session_state["detected_lang"] = detected_lang
        st.subheader("Detected Language")
        st.write(detected_lang)
    elif st.session_state["detected_lang"]:
        st.subheader("Detected Language")
        st.write(st.session_state["detected_lang"])

    if st.session_state["detected_lang"] and not st.session_state["translations"]:
        translations = translate_text(st.session_state["transcription"], st.session_state["detected_lang"])
        st.session_state["translations"] = translations

    if st.session_state["translations"]:
        st.subheader("Translations")
        for lang, translation in st.session_state["translations"].items():
            if translation:
                st.write(f"**{lang.upper()}:** {translation}")

                if st.button(f"Play {lang.upper()} Translation", key=lang):
                    with st.spinner(f"Playing translation in {lang}..."):
                        text_to_speech(translation, lang=lang)
                        st.success(f"Played {lang} translation successfully.")
            else:
                st.write(f"No valid translation available in {lang}")
else:
    st.info("Press 'Record Audio' to begin.")
