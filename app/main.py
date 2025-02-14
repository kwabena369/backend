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
    while True:  # Keep trying to restart if it crashes
        try:
            server = await websockets.serve(audio_handler, "0.0.0.0", 8000)
            print("WebSocket server started on ws://0.0.0.0:8000")
            await server.wait_closed()  # Wait until the server stops
        except Exception as e:
            print(f"WebSocket server crashed: {e}, restarting...")
            await asyncio.sleep(3)  # Wait before restarting

# Run WebSocket server in the background
asyncio.create_task(start_server())

async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        return
    if scope["type"] == "websocket":
        websocket = websockets.WebSocketServerProtocol()
        await websocket.accept()
        await audio_handler(websocket, None)
