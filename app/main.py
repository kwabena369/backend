import asyncio
import websockets

async def audio_handler(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received audio data: {len(message)} bytes")  # Log received audio size
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def start_server():
    async with websockets.serve(audio_handler, "0.0.0.0", 8000):
        print("WebSocket server started on ws://0.0.0.0:8000")
        await asyncio.Future()  # Keep running indefinitely

if __name__ == "__main__":
    asyncio.run(start_server())  # Ensure it runs in a proper event loop
