import torch
import os
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

docs = [
    "退款政策：顾客购买后 7 天内可无条件退款，需保留购物小票。",
    "请假政策：员工请假需至少提前一天向主管申请，病假需附医院证明。",
    "报销政策：差旅报销需在 30 天内提交，并附上正规发票。",
]

query = "我想请假，需要提前几天申请？"
doc_vecs = model.encode(docs)
query_vec = model.encode(query)
similarities = util.cos_sim(query_vec, doc_vecs)
print("相似度结果：", similarities)

best_idx = torch.argmax(similarities)
best_doc = docs[best_idx]
print("最相似的资料：", best_doc)

prompt = f"""请根据下面给出的公司制度资料回答用户问题。
要求：回答的最后，必须标注"来源：第 X 段"，X 是你依据的资料编号。不要编造资料里没有的内容。

资料：
第 1 段：{docs[0]}
第 2 段：{docs[1]}
第 3 段：{docs[2]}

问题：{query}"""

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}],
)
print("AI回答：", response.choices[0].message.content)
