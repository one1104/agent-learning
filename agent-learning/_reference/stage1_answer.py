import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def add(a, b):
    return a + b


ADD_TOOL = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "计算两个数字相加的结果。当用户想算加法时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一个加数"},
                "b": {"type": "number", "description": "第二个加数"},
            },
            "required": ["a", "b"],
        },
    },
}

TOOL_FUNCTIONS = {"add": add}


def run_tool(tool_call):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if name not in TOOL_FUNCTIONS:
        return f"错误：未知的工具 {name}"

    try:
        result = TOOL_FUNCTIONS[name](**args)
        return str(result)
    except Exception as e:
        return f"错误：{e}"


def run_agent(user_question, max_steps=5, verbose=True):
    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )

    messages = [{"role": "user", "content": user_question}]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=[ADD_TOOL],
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                result = run_tool(tool_call)
                if verbose:
                    print(f"[第 {step + 1} 步] 模型调用工具 "
                          f"{tool_call.function.name}({tool_call.function.arguments}) "
                          f"-> 结果: {result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
            continue

        return message.content or "（模型没有返回内容）"

    return "达到最大步数仍未完成。"


if __name__ == "__main__":
    question = input("请输入问题：").strip() or "3 加 4 等于几？"
    answer = run_agent(question)
    print("\n===== 最终答案 =====\n")
    print(answer)
