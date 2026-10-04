from abc import ABC, abstractmethod
from typing import AsyncGenerator

class LLMProvider(ABC):
    """
    大模型提供商的抽象接口。
    所有具体提供商（DeepSeek、通义千问、OpenAI）都必须实现这两个方法。
    """
    
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        """
        非流式调用，返回完整回复。
        参数：messages - 对话消息列表 [{"role": "user", "content": "你好"}]
        返回：模型的完整回复文本
        """
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """
        流式调用，逐块产出内容。
        参数：messages - 对话消息列表
        产出：每次产出一个文本块（字符串）
        """
        pass