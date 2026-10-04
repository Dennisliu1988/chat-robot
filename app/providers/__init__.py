import os
from .base import LLMProvider
from .deepseek import DeepSeekProvider
from .qwen import QwenProvider

def get_provider(name: str | None = None) -> LLMProvider:
    """
    工厂函数：根据名称返回对应的 Provider 实例。
    参数：name - 提供商名称（deepseek/qwen）。如果不传，从环境变量 LLM_PROVIDER 读取。
    """
    provider_name = name or os.getenv("LLM_PROVIDER", "deepseek")
    
    if provider_name == "deepseek":
        return DeepSeekProvider()
    elif provider_name == "qwen":
        return QwenProvider()
    else:
        raise ValueError(f"不支持的 Provider: {provider_name}")