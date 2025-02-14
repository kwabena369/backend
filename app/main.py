# app/main.py
import asyncio
import websockets
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"Received audio data: {len(data)} bytes")
    except Exception as e:
        print(f"Client disconnected: {e}")

# This is needed for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)