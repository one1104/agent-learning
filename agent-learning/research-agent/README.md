# AI 研究助手（Research Agent）

一个基于 LLM + RAG + 多智能体的研究助手。输入一个主题，它会自动检索知识库、整理研究要点、撰写研究报告、审查改进，最终输出一份带引用来源的研究报告。

## 功能特点

- **RAG 检索**：基于真实资料的向量检索，从知识库中找出与主题最相关的内容
- **多智能体协作**：研究员（researcher）→ 写作者（writer）→ 审查者（reviewer）接力完成
- **引用来源**：报告会标注每条结论的资料出处
- **审查改进**：审查者打分，低于阈值自动打回写作者改进

## 技术栈

- LLM：DeepSeek（deepseek-chat）
- RAG：sentence-transformers（paraphrase-multilingual-MiniLM-L12-v2）
- 多智能体：research → write → review → revise

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-你的key
```

### 3. 运行

```bash
python main.py
```

然后输入一个研究主题，例如"AI 对就业市场有什么影响？"。

## 项目结构

```
research-agent/
├── main.py           # 主程序：串联完整流程
├── agents.py         # 三个角色：researcher / writer / reviewer
├── rag.py            # 检索模块：向量化 + 相似度检索
├── knowledge_base.py # 知识库：7 篇 AI 主题的真实资料
├── requirements.txt  # 依赖清单
└── README.md         # 本文件
```

## 工作流程

```
用户输入主题
    ↓
rag.retrieve()  检索最相关的资料
    ↓
researcher      整理研究要点（带引用）
    ↓
writer          撰写研究报告
    ↓
reviewer        打分，低于 8 分则打回 writer 改进
    ↓
输出最终报告
```

## 示例

输入"AI 对就业市场有什么影响？"，输出一份包含引言、数据（如自动化岗位需求下降 13%、增强型岗位上升 20%）、分析和结论的完整报告，末尾附参考资料列表。

## 限制

- 知识库是预置的 7 篇资料，不是实时网络搜索
- embedding 模型在本地运行，首次运行需下载（约 400MB）
- 报告质量依赖知识库覆盖范围，超出知识库的主题无法回答

