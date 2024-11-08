import os
import sounddevice as sd
import soundfile as sf


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
