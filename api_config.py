# -*- coding: utf-8 -*-
"""
AI API配置文件
支持小米tokenplan和第三方兼容OpenAI网关
"""

# ===== 默认模型配置 =====
DEFAULT_MODEL = "xiaomi"

# ===== 模型配置字典 =====
MODELS = {
    # 小米tokenplan - 文本对话
    "xiaomi": {
        "gateway_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "api_key": "",
        "model_name": "mimo-v2.5",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30,
    },
    # 小米tokenplan - 视觉模型（图像识别）
    "xiaomi-vision": {
        "gateway_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "api_key": "",
        "model_name": "mimo-v2.5",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30,
    },
    # 第三方兼容OpenAI网关（如DeepSeek、Qwen等）
    "deepseek": {
        "gateway_url": "https://api.deepseek.com/v1",
        "api_key": "",
        "model_name": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30,
    },
    # OpenAI官方
    "openai": {
        "gateway_url": "https://api.openai.com/v1",
        "api_key": "",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30,
    },
}


def get_model_config(model_name=None):
    """
    获取指定模型的配置

    Args:
        model_name: 模型名称，不传则返回默认模型配置

    Returns:
        dict: 模型配置字典，如果模型不存在返回None
    """
    model = model_name or DEFAULT_MODEL
    return MODELS.get(model)