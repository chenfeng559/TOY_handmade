import requests
import json

# 定义API端点
API_ENDPOINT = 'https://api.coze.cn/open_api/v2/chat'

# 您的API Token
headers = {
    'Authorization': 'Bearer pat_jXnr1OiIan6okcfkn1Dn15kep6M0zXE4goJ56wC20OaO6luBsw1TPuYrTslGqMjS',  # 替换pat_XXXXXXXXXXXXXXXXXX为你的“Personal Access Tokens”
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Host': 'api.coze.cn',
    'Connection': 'keep-alive'
}

data = {
    "conversation_id": "123",
    "bot_id": "7396529566078058531",
    "user": "29032201862555",
    "query": "小青蛙",
    "stream": False
}


try:
    # 发送post请求并保存响应为响应对象
    response = requests.post(url=API_ENDPOINT, headers=headers, data=json.dumps(data), timeout=60)  # 设置超时时间为60秒

    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        print(f"响应文本：{response.text}")
    else:
        try:
            data = response.json()
            print(data)
        except json.JSONDecodeError:
            print("响应不是有效的JSON格式")
            print(f"响应文本：{response.text}")
except requests.exceptions.Timeout:
    print("请求超时，请稍后重试")
except requests.exceptions.RequestException as e:
    print(f"请求发生错误: {e}")