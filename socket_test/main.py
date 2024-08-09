import asyncio
import websockets

async def handle_connection(websocket, path):

        print("Audio path connected")
        async for message in websocket:
            print(f"Received audio data: {message[:10]}...")  # Print first 10 bytes as example
    # else:
    #     print("Echo path connected")
    #     async for message in websocket:
    #         print(f"Received message from client: {message}")
    #         await websocket.send(f"Echo: {message}")

async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())