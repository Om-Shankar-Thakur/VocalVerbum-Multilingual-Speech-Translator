import whisper


def transcribe_audio(audio_file):
    """Transcribe audio using Whisper model."""
    # Load the Whisper model
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    transcription = result['text']
    print(f"Transcription: {transcription}")
    return transcription
