import app.config  # noqa: F401 — 加载 .env
from app.models import ChatRequest, ChatResponse
from app.providers import get_provider
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="AI Chatbot API")
# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# ========== 路由 ==========
@app.get("/health")  # 健康检查路由，返回 OK
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)  # 聊天路由，接收请求，返回响应
async def chat(request: ChatRequest):
    # 把 history 和当前 message 拼成完整的 messages 列表
    messages = [{"role": msg.role, "content": msg.content} for msg in request.history]
    messages.append({"role": "user", "content": request.message})
    provider = get_provider()  # ← 自动根据 .env 选择
    reply = await provider.chat(messages)
    return ChatResponse(reply=reply)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in request.history]
    messages.append({"role": "user", "content": request.message})
    provider = get_provider()

    async def event_generator():
        async for chunk in provider.stream_chat(messages):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )