import asyncio
from fastapi import FastAPI, WebSocket
import json
from vosk import Model, KaldiRecognizer
import os
import urllib.request
import zipfile
from datetime import datetime
import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

def setup_model():
    model_name = "vosk-model-small-en-us-0.15"
    model_path = f"{model_name}"
    
    if not os.path.exists(model_path):
        logger.info("Starting model download process...")
        os.makedirs(model_path, exist_ok=True)
        
        url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
        zip_path = f"{model_name}.zip"
        
        logger.info(f"Downloading model from {url}")
        urllib.request.urlretrieve(url, zip_path)
        
        logger.info("Extracting model files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        os.remove(zip_path)
        logger.info("Model setup completed successfully!")
    else:
        logger.info("Model already exists, skipping download")
    
    return model_path

# Initialize model at startup
logger.info("Initializing Vosk model...")
model_path = setup_model()
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
logger.info("Vosk model initialized successfully!")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("New client connected to WebSocket")
    
    try:
        while True:
            try:
                # Log received data size
                data = await websocket.receive_bytes()
                logger.debug(f"Received audio chunk of size: {len(data)} bytes")
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    
                    if text:  # Only log if there's actual transcribed text
                        logger.info(f"Transcribed text: {text}")
                    else:
                        logger.debug("No text transcribed from audio chunk")
                    
                    await websocket.send_text(text)
                    
            except Exception as e:
                try:
                    data = await websocket.receive_text()
                    logger.debug(f"Received text data: {data}")
                    
                    json_data = json.loads(data)
                    if 'date' in json_data:
                        logger.info(f"Received date from frontend: {json_data['date']}")
                        await websocket.send_text(f"Date received: {json_data['date']}")
                    
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON data")
                except Exception as e:
                    logger.error(f"Error processing text data: {str(e)}")
                    
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        logger.info("Client disconnected from WebSocket")

@app.get("/")
async def root():
    logger.info("Health check endpoint accessed")
    return {"status": "ready", "message": "Speech recognition server is running"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting speech recognition server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)