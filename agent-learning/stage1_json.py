import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "user",
            "content": "我叫李雷，今年30岁，是一名软件工程师。请从中提取姓名、年龄和职业，并以JSON格式返回。",
        }
    ],
    response_format={"type": "json_object"},
)

text = response.choices[0].message.content
print("模型原始输出：", text)
data = json.loads(text)
print("姓名：", data["姓名"])
print("年龄：", data["年龄"])
print("职业：", data["职业"])
