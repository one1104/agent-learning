import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

EVAL_CASES = [
    {"question": "3 加 4 等于几？", "expected": "7"},
    {"question": "1 乘 2 加 3 等于几？", "expected": "5"},
    {"question": "10 加 0 等于几？", "expected": "10"},
    {"question": "5 乘 6 等于几？", "expected": "30"},
    {"question": "0 乘 100 等于几？", "expected": "0"},
    {"question": "12.5 加 7.5 等于几？", "expected": "20"},
    {"question": "100 加 200 等于几？", "expected": "300"},
    {"question": "负 5 加 3 等于几？", "expected": "-2"},
    {"question": "2 加 2 加 2 加 2 等于几？", "expected": "8"},
    {"question": "你好，请问今天天气怎么样？", "expected": ""},
]


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
DANGEROUS_TOOLS = set()


def run_agent(question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    trace = []

    for step in range(max_steps):
        trace.append(f"第{step + 1}步：发送请求")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=[add_tool, multiply_tool, read_file_tool],
            timeout=30,
        )
        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                name = tool_call.function.name

                if name in DANGEROUS_TOOLS:
                    print(f"⚠️ 危险操作 [{name}]")
                    allow = input("是否允许？(y/n): ")
                    if allow.lower() != "y":
                        result = "用户拒绝了该操作"
                    else:
                        result = TOOL_FUNCTIONS[name](**args)
                else:
                    result = TOOL_FUNCTIONS[name](**args)

                trace.append(f" 调用工具：{name}{args} -> {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
        else:
            trace.append(f"模型完成：{message.content}")
            return message.content, trace

    return "达到最大步数，未完成", trace


def judge(answer, expected):
    return expected in answer


passed = 0
for case in EVAL_CASES:
    answer, trace = run_agent(case["question"])
    ok = judge(answer, case["expected"])
    if ok:
        passed += 1
        print(f"✅ {case['question']} → {answer}")
    else:
        print(f"❌ {case['question']} → 期望 {case['expected']}，实际 {answer}")

print(f"\n成功率：{passed}/{len(EVAL_CASES)} = {passed/len(EVAL_CASES)*100:.0f}%")

success_rate = passed / len(EVAL_CASES)
if success_rate < 0.8:
    print(f"⚠️ 警告：成功率 {success_rate*100:.0f}% 低于阈值 80%，可能引入了退化！")
    exit(1)
else:
    print(f"✅ 回归测试通过：成功率 {success_rate*100:.0f}%")
