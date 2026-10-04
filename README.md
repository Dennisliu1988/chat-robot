# ChatRobot - 多模型 AI 对话服务

[![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![uv](https://img.shields.io/badge/package%20manager-uv-blueviolet.svg)](https://docs.astral.sh/uv/)

ChatRobot 是一个基于 **FastAPI** 构建的高性能、模块化多模型 AI 对话后端服务。支持 **DeepSeek** 与 **通义千问 (Qwen)** 等多种主流大模型的无缝接入，具备流式输出（SSE 打字机效果）、多轮对话上下文管理、结构化数据解析及容错重试能力。

---

## 🌟 功能特性

- **多 Provider 架构支持**：基于抽象基类（ABC）与工厂模式设计，支持 **DeepSeek** 与 **通义千问 (Qwen)** 热插拔切换，具备高度可扩展性。
- **打字机级流式传输（SSE）**：基于 Server-Sent Events（`text/event-stream`）实现单向流式输出，有效降低首字延迟（TTFT）。
- **轻量无状态多轮对话**：客户端维护历史上下文（Client-managed Context），服务端无状态（Stateless），原生支持水平横向扩展与负载均衡。
- **结构化输出与容错机制**：基于 Pydantic 的三层防护网（Prompt 约束 ➔ Schema 运行时校验 ➔ 错误反馈自动重试）。
- **静态资源即开即用**：内置 Web 对话演示界面，支持浏览器端直接体验打字机流式交互。
- **现代化工程工具链**：采用高性能 Python 包管理器 `uv` 进行统一的依赖管理与虚环境隔离。

---

## 🛠 技术栈

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **编程语言** | Python 3.12+ | 利用现代异步语法及原生类型注解 |
| **Web 框架** | FastAPI | 高性能异步 ASGI 框架，内置 OpenAPI 文档 |
| **HTTP 客户端** | HTTPX | 异步非阻塞 HTTP 请求，支持连接池与流式响应 |
| **数据校验** | Pydantic v2 | 强类型数据建模与高性能校验 |
| **包管理** | uv | 极速 Rust 实现的 Python 依赖管理工具 |
| **通信机制** | SSE (Server-Sent Events) | 单向实时文本流推送 |

---

## 🚀 快速开始

### 1. 克隆项目与安装依赖

项目推荐使用 [uv](https://docs.astral.sh/uv/) 管理依赖：

```bash
# 同步并安装依赖
uv sync
```

### 2. 配置环境变量

复制环境配置文件模版并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# 大模型 API Key 配置（至少配置一个）
DEEPSEEK_API_KEY=sk-xxxxxx
QWEN_API_KEY=sk-xxxxxx

# 默认使用的 Provider（可选: deepseek 或 qwen）
LLM_PROVIDER=deepseek
```

### 3. 启动开发服务器

```bash
uv run uvicorn app.main:app --reload
```

- **API 接口地址**：`http://127.0.0.1:8000`
- **Swagger 交互文档**：`http://127.0.0.1:8000/docs`
- **内置前端页面**：`http://127.0.0.1:8000/static/index.html`

---

## 🏛 核心架构设计

> 详细设计思路与权衡考量，请参阅：👉 [架构决策记录 (docs/architecture.md)](docs/architecture.md)

### 1. 为什么采用“抽象基类 + 工厂模式”？
```
                 ┌──────────────────┐
                 │  FastAPI 路由层  │
                 └─────────┬────────┘
                           │ 获取实例
                 ┌─────────▼────────┐
                 │  get_provider()  │ (工厂函数)
                 └─────────┬────────┘
                           │ 遵循统一契约
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────────┐        ┌──────────────────────┐
│   DeepSeekProvider   │        │     QwenProvider     │
│  (实现 LLMProvider)  │        │  (实现 LLMProvider)  │
└──────────────────────┘        └──────────────────────┘
```
- **解耦业务与供应商**：API 路由只需调用基类 `chat()` 或 `stream_chat()` 契约方法，无需关心具体厂商的鉴权机制和请求差异。
- **开闭原则（OCP）**：新增任何模型厂商，仅需新增对应 Provider 类并在工厂注册，主服务代码零修改。

### 2. 为什么流式输出选用 SSE 而非 WebSocket？
- **单向交互契合**：LLM 补全输出是典型的服务端向客户端单向推送场景，无需 WebSocket 的全双工双向开销。
- **网络基础设施友好**：SSE 遵循标标准 HTTP 协议，完美兼容现有的反向代理、负载均衡、认证中间件与防火墙策略。
- **低延迟轻量化**：免除复杂长连接握手与协议升级，首字延迟更低，客户端重连机制更稳健。

### 3. 为什么多轮对话由客户端维护历史？
- **服务端无状态（Stateless）**：避免了服务端内存 Session 或分布式锁的复杂度，服务节点可随时伸缩扩容。
- **灵活性**：客户端可自主控制滑动窗口与携带历史轮数，保障上下文 Token 预算。

---

## 📡 API 接口规范

### 1. 健康检查
- **路径**：`GET /health`
- **响应**：`{"status": "ok"}`

### 2. 普通同步对话
- **路径**：`POST /chat`
- **请求体（JSON）**：
  ```json
  {
    "message": "什么是工厂模式？",
    "history": [
      {"role": "user", "content": "你好"},
      {"role": "assistant", "content": "你好！有什么我可以帮你的？"}
    ]
  }
  ```
- **响应体（JSON）**：
  ```json
  {
    "reply": "工厂模式是一种创建型设计模式..."
  }
  ```

### 3. 流式对话（SSE）
- **路径**：`POST /chat/stream`
- **媒体类型**：`text/event-stream`
- **事件流示例**：
  ```text
  data: 你
  data: 好
  data: ，
  data: 我
  data: 是
  data: AI
  data: [DONE]
  ```

---

## 📂 项目结构

```
chatRobot/
├── app/                          # 核心应用源码
│   ├── __init__.py
│   ├── config.py                 # 环境配置加载 (.env)
│   ├── main.py                   # FastAPI 应用入口与路由定义
│   ├── models.py                 # Pydantic 请求与响应数据契约
│   ├── providers/                # 多模型 Provider 模块
│   │   ├── __init__.py           # 工厂函数 get_provider
│   │   ├── base.py               # 抽象基类 LLMProvider
│   │   ├── deepseek.py           # DeepSeek 实现
│   │   └── qwen.py               # 通义千问实现
│   └── services/                 # 业务逻辑层（预留后续会话与存储扩展）
│       └── __init__.py
├── scripts/                      # 测试、探索与实验脚本
│   ├── analyze_resume.py         # 结构化输出/Prompt/CoT/Pydantic防御实验
│   └── stream_test.py            # Provider 流式功能验证脚本
├── static/                       # 静态资源与前端页面
│   └── index.html                # 前端对话界面
├── tests/                        # 单元测试与集成测试
│   └── __init__.py
├── docs/                         # 架构与技术文档
│   └── architecture.md           # 架构决策记录 (ADR)
├── .env                          # 本地环境变量（已加入 .gitignore）
├── .env.example                  # 环境变量示例
├── .gitignore
├── pyproject.toml                # 项目元数据与依赖定义
├── uv.lock                       # 依赖版本锁定文件
└── README.md                     # 项目介绍与快速开始文档
```

---

## 🧪 测试脚本运行

通过 `scripts/` 中的脚本可独立验证模型能力：

```bash
# 测试当前 Provider 的流式输出能力
uv run python -m scripts.stream_test

# 运行简历结构化解析与重试机制实验
uv run python -m scripts.analyze_resume
```

---

## 🗺 后续演进计划 (Roadmap)

- [ ] **会话持久化与管理**：引入 SQLite / PostgreSQL，支持多会话切换、历史漫游与持久化存储。
- [ ] **高并发限流与缓存**：使用 Redis 缓存常见高频问答，降低大模型 API 调用成本。
- [ ] **用户认证与安全鉴权**：增加 JWT 认证，支持用户个人会话隔离与配额控制。
- [ ] **容器化与部署**：提供 Dockerfile 与 docker-compose 配置，支持一键容器化交付。
- [ ] **自动化测试集**：编写基于 pytest 与 pytest-asyncio 的测试用例，覆盖各大核心路由与异常边界。
