from sentence_transformers import SentenceTransformer, util
from knowledge_base import DOCUMENTS

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def embed(text):
    """文本转向量"""
    return model.encode(text)


def retrieve(query, top_k=3):
    """从知识库检索与 query 最相关的 top_k 篇文档"""
    doc_texts = [doc["content"] for doc in DOCUMENTS]
    doc_vecs = model.encode(doc_texts)

    query_vec = embed(query)

    similarities = util.cos_sim(query_vec, doc_vecs)[0]

    ranked = sorted(
        range(len(DOCUMENTS)),
        key=lambda i: similarities[i],
        reverse=True,
    )

    results = []
    for i in ranked[:top_k]:
        results.append(DOCUMENTS[i])

    return results