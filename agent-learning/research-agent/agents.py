import json
import os
from rag import retrieve
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

def researcher(question):
    docs = retrieve(question, top_k=3)

    material = ""
    for i, doc in enumerate(docs, start=1):
        material += f"资料{i}：\n标题：{doc['title']}\n来源：{doc['source']}\n内容：{doc['content']}\n\n"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是研究员。根据提供的资料，整理出 3-5 条研究要点，每条注明来自哪份资料（标题）。"},
            {"role": "user", "content": f"研究主题：{question}\n\n资料如下：\n{material}"},
        ],
    )
    return response.choices[0].message.content


def writer(question, key_points):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是写作者。根据研究要点，写一份结构清晰的研究报告，包含标题、正文、结尾的引用来源列表。"},
            {"role": "user", "content": f"研究主题：{question}\n\n研究要点：\n{key_points}"},
        ],
    )
    return response.choices[0].message.content


def reviewer(report):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是严格的审查者。给报告打分，只输出一个 1-10 的整数，不要输出其他文字。"},
            {"role": "user", "content": f"报告如下：\n{report}"},
        ],
    )
    return response.choices[0].message.content.strip()