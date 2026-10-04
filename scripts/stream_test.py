# scripts/stream_test.py
"""
学习测试脚本：测试多 Provider 流式输出能力。
使用方式：
    uv run python -m scripts.stream_test
"""
import asyncio
import app.config  # noqa: F401 — 加载 .env
from app.providers import get_provider


async def main():
    provider = get_provider()
    print(f"========================================")
    print(f"正在测试 Provider: {provider.__class__.__name__}")
    print(f"========================================")
    print("模型输出: ", end="", flush=True)

    messages = [{"role": "user", "content": "你好，请用一句话介绍你自己"}]
    async for chunk in provider.stream_chat(messages):
        print(chunk, end="", flush=True)
    print("\n\n[测试完成]")


if __name__ == "__main__":
    asyncio.run(main())
