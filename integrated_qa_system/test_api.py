import requests
import json

url = "http://127.0.0.1:8000/query"
data = {
    "query": "什么是AI?",
    "session_id": None,
    "source_filter": None
}

response = requests.post(url, json=data, stream=True)

print("开始接收响应：\n")
for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        if decoded_line.startswith('data: '):
            json_str = decoded_line[6:]
            try:
                data = json.loads(json_str)
                if 'token' in data and data['token']:
                    print(data['token'], end='', flush=True)
                if data.get('is_complete'):
                    print("\n\n✅ 回答完成")
                    break
            except Exception as e:
                print(f"\n错误: {e}")
