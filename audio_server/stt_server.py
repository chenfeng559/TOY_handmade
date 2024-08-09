from flask import Flask, request, jsonify
import speech_recognition as sr
import base64

app = Flask(__name__)

@app.route('/receive_audio', methods=['POST'])
def receive_audio():
    data = request.json  # 获取录音数据
    # 调用语音识别服务处理audio_data
    
    base64_audio_data = data['audio_data']  # 从JSON中获取Base64编码的音频数据  
    

    audio_data = base64.b64decode(base64_audio_data)  # 解码Base64数据
    
    # 调用语音识别服务处理audio_data
    recognition_result = process_speech_recognition(audio_data)
    
    # 返回识别结果
    return jsonify({"result": recognition_result})

def process_speech_recognition(audio_data):
    # 这里是调用语音识别服务的逻辑，可以使用现有的recognize_speech函数或其他服务
    # 假设recognize_speech函数返回识别的文本
    return sr.recognize_speech(audio_data,APPID='68c6d108',
        APISecret='YjAyN2QxM2JjZDUwNmRlMTYxZDExYTE4',
        APIKey='d05347012a653385c38b8d877d844344')

if __name__ == "__main__":
    app.run()