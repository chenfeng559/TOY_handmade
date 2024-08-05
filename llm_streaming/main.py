from openai import OpenAI
import configparser
import json

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
        # 可选，配置以后会在流式输出的最后一行展示token使用信息
        stream_options={"include_usage": True},
        temperature=0.8,
        top_p=0.8
        )
    for chunk in completion:
        a= chunk.model_dump_json()
        result_dict = json.loads(a)
        if result_dict['choices'][0]['finish_reason'] == 'stop':
            break
        print(result_dict['choices'][0]['delta']['content'])

if __name__ == '__main__':
        user_input = input("请输入：")
        # 将用户问题信息添加到messages列表中
        messages = [{'role': 'system', 'content': '你是一个故事机，用于讲述给小孩子听的故事'}]
        messages.append({'role': 'user', 'content': user_input})
        assistant_output = get_response(messages)
    

