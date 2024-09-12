import os
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from speechbrain.inference.ASR import EncoderDecoderASR

# Load environment variables
load_dotenv()

# Ensure the audio directory exists
os.makedirs("audio", exist_ok=True)

# Load the Facebook SpeechBrain ASR model
asr_model = EncoderDecoderASR.from_hparams(
    source="speechbrain/asr-crdnn-commonvoice-14-es", savedir="pretrained_models/asr-crdnn-commonvoice-14-es")


def record_audio(duration, sample_rate=16000):
    """Record audio using the microphone."""
    print("Recording...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    print("Recording completed")
    return audio_data


def save_audio(filename, audio_data, sample_rate=16000):
    """Save the recorded audio to a file."""
    sf.write(filename, audio_data, sample_rate)
    print(f"Audio saved to {filename}")


def transcribe_audio(audio_file):
    """Transcribe the recorded audio using the SpeechBrain model."""
    print(f"Transcribing audio file: {audio_file}")
    transcription = asr_model.transcribe_file(audio_file)
    print(f"Transcription: {transcription}")
    return transcription


# Example usage of recording and transcribing
if __name__ == "__main__":
    duration = 10  # Set the duration of recording (in seconds)
    audio_data = record_audio(duration)
    audio_file = "audio/input.wav"
    save_audio(audio_file, audio_data)
    transcription = transcribe_audio(audio_file)
