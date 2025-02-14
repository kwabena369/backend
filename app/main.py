import asyncio
import websockets
from fastapi import FastAPI, WebSocket
import json
from vosk import Model, KaldiRecognizer
import wave

app = FastAPI()

# Load the Vosk model
model = Model("vosk-model/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)  # Assuming 16kHz audio input

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    try:
        while True:
            data = await websocket.receive_bytes()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                print(f"Transcribed text: {text}")
                await websocket.send_text(text)  # Send text back to the frontend
    except Exception as e:
        print(f"Client disconnected: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
