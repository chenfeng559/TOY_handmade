import yaml

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

import requests
import json

url = "https://api.coze.cn/v1/space/published_bots_list"

params = {
    "space_id": "7394742609157423138",
}
headers = {
    'Authorization': 'Bearer pat_jXnr1OiIan6okcfkn1Dn15kep6M0zXE4goJ56wC20OaO6luBsw1TPuYrTslGqMjS',  # 替换pat_XXXXXXXXXXXXXXXXXX为你的“Personal Access Tokens”
    'Content-Type': 'application/json',
}

response = requests.get(url, headers=headers, params=params)

print(response.status_code)
print(response.text)