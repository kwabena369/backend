import asyncio
import websockets

async def audio_handler(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received audio data: {len(message)} bytes")  # Log received audio size
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def app(scope, receive, send):  # ASGI entry point
    if scope["type"] == "lifespan":
        return  # Handle lifespan events if needed

    if scope["type"] == "websocket":
        websocket = websockets.WebSocketServerProtocol()
        await websocket.accept()
        await audio_handler(websocket, None)

# Start WebSocket server in a separate task
async def start_server():
    server = await websockets.serve(audio_handler, "0.0.0.0", 8000)
    print("WebSocket server started on ws://0.0.0.0:8000")
    await server.wait_closed()

# Run the WebSocket server in the background
asyncio.create_task(start_server())
