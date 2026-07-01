# -*- coding: utf-8 -*-
"""
AI对话模块
调用AI API分析截图并返回引导指令
"""
import base64
import json
import requests
from api_config import get_model_config

SYSTEM_PROMPT = """你是Nuke智能助手。用户会发送Nuke界面截图和问题。

【重要规则】你必须且只能返回一个JSON对象，不要返回任何其他文字、解释、代码块标记。

JSON格式如下：
{"answer":"简短回答","steps":[{"x":数字,"y":数字,"text":"文字"}]}

规则：
1. answer：简短回答用户问题（一句话）
2. steps：引导点数组，每个点包含x（整数）、y（整数）、text（一句话）
3. x和y必须是整数类型的像素坐标，不能是数组、字符串或其他类型
4. 如果不需要引导，steps为空数组：[]
5. 不要用```json```包裹，直接返回JSON
6. 不要在JSON前后添加任何文字

正确示例：
{"answer":"点击Roto节点的brush size滑块即可调整笔刷大小","steps":[{"x":500,"y":300,"text":"点击这里调整笔刷大小"}]}

错误示例（不要这样返回）：
以下是回答：{"answer":...}
或
```json
{"answer":...}
```"""


def image_to_base64(image_path):
    """图片转Base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_prompt(question, base64_image):
    """构建AI请求消息"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": [
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ]}
    ]


def parse_ai_response(response_text):
    """解析AI返回的JSON"""
    import re
    text = response_text.strip()

    # 去掉markdown代码块标记
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    try:
        result = json.loads(text)
        if "answer" in result:
            print(f"[AI] 直接JSON解析成功")
            return result
    except json.JSONDecodeError:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            result = json.loads(json_str)
            if "answer" in result:
                print(f"[AI] 提取JSON解析成功")
                return result
    except json.JSONDecodeError as e:
        print(f"[AI] JSON解析失败: {e}")
        print(f"[AI] 原始文本前200字符: {text[:200]}")

    return {"answer": text[:200], "steps": []}


def ask_ai(question, screenshot_path, model_name="xiaomi-vision"):
    """调用AI分析截图"""
    import logger
    config = get_model_config(model_name)
    if not config:
        return {"answer": "AI配置错误", "steps": []}

    logger.log(f"[AI] question={question}, model={model_name}")
    base64_image = image_to_base64(screenshot_path)
    messages = build_prompt(question, base64_image)

    try:
        response = requests.post(
            f"{config['gateway_url']}/chat/completions",
            headers={"Authorization": f"Bearer {config['api_key']}"},
            json={
                "model": config["model_name"],
                "messages": messages,
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"]
            },
            timeout=config["timeout"]
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        logger.log(f"[AI] raw response: {content[:300]}")
        result = parse_ai_response(content)
        logger.log(f"[AI] parsed: {result}")
        return result
    except Exception as e:
        logger.log(f"[AI] request failed: {e}")
        return {"answer": f"AI请求失败: {str(e)}", "steps": []}
