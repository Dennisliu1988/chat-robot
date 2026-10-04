# Pydantic 模型（ChatMessage/ChatRequest/ChatResponse）
from pydantic import BaseModel

class ChatMessage(BaseModel): # 消息数据模型，包含角色和内容
    role: str          # "user" 或 "assistant"
    content: str

class ChatRequest(BaseModel): # 请求数据模型，包含用户消息和历史对话
    message: str
    history: list[ChatMessage] = []

class ChatResponse(BaseModel): # 响应数据模型，包含助手回复
    reply: str