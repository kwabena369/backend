import asyncio
import signal
from websockets import serve

async def audio_handler(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received audio data: {len(message)} bytes")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def health_check(path, request_headers):
    if path == "/healthz":
        return 200, [], b"OK\n"

async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with serve(
        audio_handler,
        host="",
        port=8080,
        process_request=health_check,
    ):
        await stop

if __name__ == "__main__":
    asyncio.run(main())
