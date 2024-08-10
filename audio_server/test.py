import asyncio
import websockets
import audio_convert
import speech_recognition as sr
import  llm 

async def handle_connection(websocket, path):
    print("音频路径已连接")
    pcm_file = None

    try:
        async for message in websocket:
            if message == "START":
                pcm_file = open("output.pcm", "wb")
                print("开始接收音频数据，开始保存")
            elif message == "END":
                if pcm_file:
                    pcm_file.close()
                    print("音频数据停止发送，结束保存,开始转存")
                    audio_convert.convert_audio("output.pcm", "pcm_16k.pcm")
                    print("转存完成，开始识别")
                    result = sr.recognize_speech(
        APPID='68c6d108',
        APISecret='YjAyN2QxM2JjZDUwNmRlMTYxZDExYTE4',
        APIKey='d05347012a653385c38b8d877d844344',
        AudioFile=r'E:\WorkStation\TOY\pcm_16k.pcm'
    )
                    print(f"音频识别完成，结果为\n:{result}")  

                    user_input = str(result)
                    # 将用户问题信息添加到messages列表中
                    messages = [{'role': 'system', 'content': '你是一个故事机，用于讲述给小孩子听的故事'}]
                    messages.append({'role': 'user', 'content': user_input})
                    assistant_output = llm.get_response(messages)

                pcm_file = None
            else:
                if pcm_file:
                    if isinstance(message, (bytes, bytearray)):
                        # print(f"接收到音频数据: {message[:10]}...")  # 示例打印前10个字节
                        pcm_file.write(message)
                    else:
                        print("接收到非二进制数据。wrong")

    except websockets.exceptions.ConnectionClosed:
        print("连接已关闭")
        if pcm_file:
            pcm_file.close()

async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("WebSocket服务器已启动: ws://0.0.0.0:8765")
        await asyncio.Future()  # 永远运行

if __name__ == "__main__":
    asyncio.run(main())