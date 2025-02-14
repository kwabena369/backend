import whisper

model = whisper.load_model("tiny")

def transcribe_audio(audio_data):
    # Assuming audio_data is in a format that Whisper can process
    result = model.transcribe(audio_data)
    return result["text"]
