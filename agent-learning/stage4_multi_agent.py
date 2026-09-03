import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

plan = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个规划者。把给定的主题拆成3个要点，只输出要点列表"},
        {"role": "user", "content": "主题：AI对生活的影响"},
    ],
).choices[0].message.content

essay = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个写作者。根据给定要点写一篇 200 字短文。"},
        {"role": "user", "content": f"要点如下：\n{plan}"},
    ],
).choices[0].message.content

for round_num in range(3):
    review = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个严格的审查者。给文章打分，只输出一个 1-10 的整数。"},
            {"role": "user", "content": f"文章如下：\n{essay}"},
        ],
    ).choices[0].message.content

    score = int(review.strip())
    print(f"第{round_num + 1}轮审查：{score}分")
    if score >= 8:
        print("审查通过！")
        break

    essay = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个写作者。根据审查分数，直接输出改进后的文章，不要输出建议等其他任何文字。"},
            {"role": "user", "content": f"当前文章：\n{essay}\n\n审查分数：{score}分（满分10分）。请改进，并输出全文。"},
        ],
    ).choices[0].message.content

print("\n=== 最终文章 ===")
print(essay)
print("\n=== 最终分数 ===")
print(score, "分")
