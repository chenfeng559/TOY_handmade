from flask import Flask, request, Response, stream_with_context
from openai import OpenAI
import configparser
import json

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

def get_response(messages):
    client = OpenAI(
        api_key=config.get('dashscope', 'apiKey'),
        base_url=config.get('dashscope', 'baseUrl'),
    )
    completion = client.chat.completions.create(
        model="qwen-turbo",
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        temperature=0.8,
        top_p=0.8
    )

    def generate():
        for chunk in completion:
            a = chunk.model_dump_json()
            result_dict = json.loads(a)
            yield json.dumps(result_dict) + "\n"
            if result_dict['choices'][0]['finish_reason'] == 'stop':
                break

    return Response(stream_with_context(generate()), content_type='application/json')

@app.route('/stream_chat', methods=['POST'])
def stream_chat():
    user_input = request.json.get('message')
    if not user_input:
        return Response(json.dumps({"error": "No message provided"}), status=400, content_type='application/json')

    messages = [{'role': 'system', 'content': '你是一个故事机，用于讲述给小孩子听的故事'}]
    messages.append({'role': 'user', 'content': user_input})
    return get_response(messages)

if __name__ == '__main__':
    app.run(debug=True)