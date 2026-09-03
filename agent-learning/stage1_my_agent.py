import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


def multiply(a, b):
    return a * b


multiply_tool = {
    "type": "function",
    "function": {
        "name": "multiply",
        "description": "计算两个数字的乘积",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
    },
}


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


read_file_tool = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "读取指定路径的文件内容",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
            },
            "required": ["path"],
        },
    },
}


def add(a, b):
    return a + b


add_tool = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "计算两个数字的和",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
    },
}

TOOL_FUNCTIONS = {"add": add, "multiply": multiply, "read_file": read_file}

messages = [{"role": "user", "content": "1 乘 2 加 3 等于几？"}]
max_steps = 5
DANGEROUS_TOOLS = {"multiply"}

for step in range(max_steps):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[add_tool, multiply_tool, read_file_tool],
        timeout=30,
    )
    message = response.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            name = tool_call.function.name

            if name in DANGEROUS_TOOLS:
                print(f"模型想执行危险操作 [{name}]")
                allow = input("是否继续执行？(y/n): ")
                if allow.lower() != "y":
                    result = "用户拒绝执行危险操作，终止。"
                else:
                    result = TOOL_FUNCTIONS[name](**args)
            else:
                result = TOOL_FUNCTIONS[name](**args)

            print("工具结果: ", name, "->", result)
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })
    else:
        print(message.content)
        break
else:
    print("达到最大步骤数，未能得到最终答案。")
