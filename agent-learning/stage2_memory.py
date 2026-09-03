import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


def summarize(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个总结助手。"},
            {"role": "user", "content": str(messages)},
        ],
    )
    return response.choices[0].message.content


def save_session(messages, filename="memory.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def load_session(filename="memory.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


messages = load_session()

while True:
    user_input = input("你：")
    if user_input in ["退出", "quit"]:
        break

    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    reply = response.choices[0].message.content
    print("agent:", reply)
    messages.append({"role": "assistant", "content": reply})

    if len(messages) > 6:
        old = messages[:-2]
        recent = messages[-2:]
        summary = summarize(old)
        messages = [{"role": "system", "content": f"以下是对话的总结：{summary}"}] + recent
        print(" (已压缩历史，当前", len(messages), "条消息)")

save_session(messages)
