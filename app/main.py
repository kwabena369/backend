# app/main.py
import asyncio
from fastapi import FastAPI, WebSocket
import json
from vosk import Model, KaldiRecognizer
import os
import urllib.request
import zipfile

app = FastAPI()

# Function to download and setup model
def setup_model():
    model_name = "vosk-model-small-en-us-0.15"
    model_path = f"{model_name}"
    
    if not os.path.exists(model_path):
        print("Downloading model...")
        # Create models directory
        os.makedirs(model_path, exist_ok=True)
        
        # Download the model
        url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
        zip_path = f"{model_name}.zip"
        
        urllib.request.urlretrieve(url, zip_path)
        
        # Extract the model
        print("Extracting model...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Cleanup
        os.remove(zip_path)
        print("Model setup complete!")
    
    return model_path

# Initialize model at startup
print("Setting up Vosk model...")
model_path = setup_model()
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
print("Vosk model loaded successfully!")

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
                await websocket.send_text(text)
    except Exception as e:
        print(f"Client disconnected: {e}")

@app.get("/")
async def root():
    return {"status": "ready", "message": "Speech recognition server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)