import asyncio
import edge_tts

async def handle_edge_tts(text):
    voice = "zh-CN-XiaoyiNeural"
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk['type'] == "audio" and chunk['data'] is not None:
            try:
                yield chunk["data"]
            except Exception as e:
                print(str(e))
        elif chunk['type'] == "WordBoundary":
            print("end")
