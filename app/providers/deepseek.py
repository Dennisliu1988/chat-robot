import os
import json
import httpx
from typing import AsyncGenerator
from .base import LLMProvider

class DeepSeekProvider(LLMProvider):
    """DeepSeek 大模型提供商"""
    
    def __init__(self):
        # 从环境变量读取 API Key
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        # API 地址和模型名，写在类里方便后续修改
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
    
    async def chat(self, messages: list[dict]) -> str:
        """非流式调用"""
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def stream_chat(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """流式调用"""
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置")
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages, "stream": True},
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]