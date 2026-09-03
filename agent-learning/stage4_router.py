import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

knowledge = {
    "AI 最新进展": "2025 年以来，大模型在多模态、Agent 能力、推理效率上持续突破...",
    "AI 就业影响": "研究显示，AI 正在自动化部分重复性工作，同时创造新岗位...",
}

user_question = input("你的问题：")

route = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是路由器。判断用户问题该交给谁处理，只输出两个词之一：「研究」或「写作」。如果用户想了解事实/查资料，输出「研究」；如果用户想生成文章/内容，输出「写作」。"},
        {"role": "user", "content": user_question},
    ],
).choices[0].message.content.strip()

print("Router 判断：", route)

if route == "研究":
    answer = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个研究员。根据提供的资料回答用户问题。"},
            {"role": "user", "content": f"问题：{user_question}\n资料：{knowledge.get('AI 最新进展', '')}"},
        ],
    ).choices[0].message.content
    print("研究 agent 回答：", answer)

elif route == "写作":
    essay = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个写作者。根据主题写一篇短文。"},
            {"role": "user", "content": user_question},
        ],
    ).choices[0].message.content
    print("写作 agent 回答：", essay)
