import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

browser = None
page = None
playwright = None
action_log = []

ALLOWED_DOMAINS = ["example.com", "baidu.com", "demo.playwright.dev"]


def start_browser():
    global browser, page, playwright
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch()
    page = browser.new_page()
    return "浏览器已启动"


def log_action(action):
    action_log.append(action)
    print(f"[日志] {action}")


def open_url(url):
    if not any(domain in url for domain in ALLOWED_DOMAINS):
        log_action(f"拒绝访问 {url}")
        return f"拒绝访问 {url}：不在允许访问的列表里"

    page.goto(url, timeout=30000)
    log_action(f"打开 {url}")
    return f"已打开 {url}"


def get_page_text(dummy=""):
    return page.inner_text("body")


def fill_input(selector, text):
    try:
        page.wait_for_selector(selector, timeout=5000)
        page.fill(selector, text)
        log_action(f"在 {selector} 输入 {text}")
        return f"已在 {selector} 输入 {text}"
    except Exception as e:
        log_action(f"输入失败：{e}")
        return f"输入失败：{e}"


def click_element(selector):
    try:
        page.wait_for_selector(selector, timeout=5000)
        page.click(selector)
        log_action(f"点击 {selector}")
        return f"已点击 {selector}"
    except Exception as e:
        log_action(f"点击失败：{e}")
        return f"点击失败：{e}"


def take_screenshot(path="screenshot.png"):
    page.screenshot(path=path)
    log_action(f"截图保存到 {path}")
    return f"已截图保存到 {path}"


open_url_tool = {
    "type": "function",
    "function": {
        "name": "open_url",
        "description": "打开一个网址。当用户想访问某个网站时，先调用这个工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "要访问的网址，例如 https://example.com"},
            },
            "required": ["url"],
        },
    },
}

get_page_text_tool = {
    "type": "function",
    "function": {
        "name": "get_page_text",
        "description": "读取当前页面上的文字内容。当用户想知道网页上有什么时使用。",
        "parameters": {"type": "object", "properties": {}},
    },
}

fill_input_tool = {
    "type": "function",
    "function": {
        "name": "fill_input",
        "description": "在网页的输入框里输入文字。selector 是输入框的选择器，text 是要输入的内容。",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "输入框的选择器，例如 #kw"},
                "text": {"type": "string", "description": "要输入的文字"},
            },
            "required": ["selector", "text"],
        },
    },
}

click_element_tool = {
    "type": "function",
    "function": {
        "name": "click_element",
        "description": "点击网页上的一个元素。selector 是要点击元素的选择器。",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "要点击元素的选择器"},
            },
            "required": ["selector"],
        },
    },
}

take_screenshot_tool = {
    "type": "function",
    "function": {
        "name": "take_screenshot",
        "description": "把当前页面截图保存到文件。当用户想看当前页面长什么样时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "截图保存的文件路径"},
            },
            "required": ["path"],
        },
    },
}

TOOL_FUNCTIONS = {
    "open_url": open_url,
    "get_page_text": get_page_text,
    "fill_input": fill_input,
    "click_element": click_element,
    "take_screenshot": take_screenshot,
}


def run_agent(question, max_steps=6):
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=[
                open_url_tool,
                get_page_text_tool,
                fill_input_tool,
                click_element_tool,
                take_screenshot_tool,
            ],
            timeout=30,
        )
        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                name = tool_call.function.name
                result = TOOL_FUNCTIONS[name](**args)
                print(f"调用工具 {name}({args}) -> 前100字: {str(result)[:100]}...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
        else:
            return message.content

    return "达到最大步数，未完成"


if __name__ == "__main__":
    start_browser()
    question = input("你想让我浏览什么网页？：").strip() or "帮我看看 https://example.com 是干嘛的"
    answer = run_agent(question)
    print("\n===== 最终回答 =====\n")
    print(answer)
