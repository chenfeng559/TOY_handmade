from flask_socketio import SocketIO, emit
from app.service.LLM.ollama_service import Ollama
from app.service.TTS.edge_tts_service import handle_edge_tts
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import string

logging.basicConfig(level=logging.DEBUG)

# 定义包含所有英文和中文标点符号的字符串
punctuation = string.punctuation + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～、〃《》「」『』【】〒〓〔〕〝〞︶︵︿﹀﹁﹂﹃﹄︻︼︷︸︹︺︽︾﹏—…"

def register_socketio_events(socketio, app):
    @socketio.on('connect')
    def handle_connect():
        logging.debug('Client connected')
        emit('response', {'data': 'Connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        logging.debug('Client disconnected')

    @socketio.on('text')
    def handle_text(data):
        logging.debug(f'Received message: {data}')
        message = data

        async def process_text(message):
            try:
                ollama = app.ollama
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    response_generator = await loop.run_in_executor(pool, ollama.chat_with_ollama, message)
                    for response in response_generator:
                        logging.debug(f"LLM response ===========> {response}")

                        # 检查响应内容是否仅包含标点符号
                        if all(char in punctuation for char in response.strip()):
                            logging.debug("Response is only punctuation, skipping TTS conversion. The char is =====>", response)
                            continue

                        # Emit LLM 返回结果(业务不需要，可以注释)
                        # socketio.emit('response', {'data': response}, json=True)

                        # 生成TTS语音数据
                        async for audio_chunk in handle_edge_tts(response):
                            logging.debug("Emitting audio chunk")
                            socketio.emit('audio', audio_chunk)
            except Exception as e:
                logging.error(f"Error in handle_text: {str(e)}")
                socketio.emit('response', {'data': f"Error - {str(e)}"})

        asyncio.run(process_text(message))

    @socketio.on('chat')
    def handle_chat(data):
        logging.debug(f'Received custom event: {data}')
        emit('response', {'data': 'Custom event received: ' + data}, broadcast=True)
