from flask import Flask
from flask_socketio import SocketIO, send
from flask_cors import CORS
import asyncio
import edge_tts


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading',logging=True,engineio_logger = True,cors_allowed_origins='*')

@socketio.on('connect')
def connect():
    print('Client connected')
    send ("你已经成功连接至服务器", broadcast=True)

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
    send ("你已经成功断开连接至服务器", broadcast=True)


@socketio.on("text")
def handle_text(text):
    asyncio.run(handle_edge_tts(text))


async def handle_edge_tts(text):
    voice = "zh-CN-XiaoyiNeural"
    comunicate = edge_tts.Communicate(text,voice)
    count = 0
    async for chunk in comunicate.stream():
        if chunk['type'] == "audio":
            # print(chunk["data"])c
            try:
                socketio.emit("count", count)
                socketio.emit("audio", chunk["data"])
                # count = count + 1     
            except Exception as e:
                print(str(e))
                print(socketio is None, chunk["data"])
        elif chunk['type'] == "WordBoundary":
            print(chunk)
            # break


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000,debug=False)