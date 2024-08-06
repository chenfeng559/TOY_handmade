import json
from openai import OpenAI

class Ollama:
    def __init__(self, host, port, model):
        self.host = host
        self.port = port
        self.base_url = f'http://{host}:{port}/v1/'
        self.model = model
        self.client = OpenAI(
            base_url=self.base_url,
            api_key='ollama',
        )

    def chat_with_ollama(self, message):
        completion = self.client.chat.completions.create(
            messages=[
                {
                    'role': 'user',
                    'content': message,
                }
            ],
            model=self.model,
            stream=True
        )
        for chunk in completion:
            result_dict = json.loads(chunk.model_dump_json())
            content = result_dict['choices'][0]['delta'].get('content', '')
            yield content + "\n"
            if result_dict['choices'][0]['finish_reason'] == 'stop':
                break
