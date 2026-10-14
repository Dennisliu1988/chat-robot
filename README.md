<a id="top" name="top"></a>

# ChatRobot - Multi-Provider LLM Dialogue Service Framework

<div align="center">

### [🇬🇧 English](#top) &nbsp; | &nbsp; [🇨🇳 简体中文](#chinese)

[![Python Version](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Package Manager](https://img.shields.io/badge/Package%20Manager-uv-blueviolet?style=flat-square)](https://docs.astral.sh/uv/)
[![Streaming](https://img.shields.io/badge/Streaming-SSE-blue?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

**ChatRobot** is a high-performance, production-ready, modular multi-provider AI chat backend framework built with **FastAPI** and **Python 3.12+**. Designed around clean abstractions and the Factory Pattern, it enables seamless hot-swapping between prominent LLM providers like **DeepSeek** and **Alibaba Qwen (通义千问)**. It features low-latency typewriter streaming via Server-Sent Events (SSE), lightweight stateless multi-turn dialogue management, and a robust 3-layer structured output defense system powered by Pydantic.

---

## 🌟 Key Features

- 🔌 **Unified Multi-Provider Architecture**: Built on Abstract Base Classes (ABC) and Factory Pattern, fully isolating vendor-specific API nuances. Switch providers on the fly via simple configuration.
- ⚡ **Low-Latency Streaming (SSE)**: Leverages Server-Sent Events (`text/event-stream`) to stream tokens in real-time, drastically reducing Time to First Token (TTFT) with a smooth typewriter UX.
- 🌐 **Stateless & Scalable**: Adopts a client-managed context approach—the server remains completely stateless, offering effortless horizontal scaling and load balancing.
- 🛡️ **3-Layer Structured Output Defense**:
  1. *Prompt-level constraint*: Strict system prompts and format instructions;
  2. *Runtime schema validation*: Pydantic v2 strict type validation and sanitization;
  3. *Self-healing retry*: Graceful error capture and feedback retry loop.
- 🖥️ **Out-of-the-Box Web UI**: Includes a modern dark-mode interactive web chat interface for immediate streaming validation.
- 🚀 **Modern Python Toolchain**: Built with Astral's blazingly fast `uv` package manager for instant dependency resolution and reproducible virtual environments.

---

## 🛠️ Tech Stack

| Domain                 | Technology               | Description                                                                            |
| :--------------------- | :----------------------- | :------------------------------------------------------------------------------------- |
| **Language**           | Python 3.12+             | Leverages modern `async`/`await` primitives and strict type annotations                |
| **Web Framework**      | FastAPI                  | High-performance ASGI framework with automatic OpenAPI / Swagger generation            |
| **HTTP Client**        | HTTPX                    | Fully asynchronous, non-blocking HTTP client supporting connection pools and streaming |
| **Data Validation**    | Pydantic v2              | Industry-standard schema validation, serialization, and error tracing                  |
| **Streaming Protocol** | SSE (Server-Sent Events) | Native HTTP unidirectional event stream, lightweight and firewall/proxy friendly       |
| **Package Manager**    | uv                       | Blazing fast Python package manager written in Rust                                    |

---

## 🏛️ Architecture & Design Philosophy

> 📘 For deep architectural context and decision tradeoffs, check out: [Architecture Decision Record (docs/architecture.md)](docs/architecture.md)

### 1. Abstract Base Class + Factory Pattern

```
                    ┌─────────────────────────┐
                    │      FastAPI Router     │
                    │  (/chat, /chat/stream)  │
                    └────────────┬────────────┘
                                 │ invokes
                    ┌────────────▼────────────┐
                    │     get_provider()      │ (Factory Function)
                    └────────────┬────────────┘
                                 │ depends on abstraction (DIP)
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│        DeepSeekProvider         │   │          QwenProvider           │
│   (implements LLMProvider)      │   │   (implements LLMProvider)      │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

- **Decoupled Business Logic**: The route handlers only depend on abstract `LLMProvider` contracts (`chat()`, `stream_chat()`), decoupled from vendor request formats or auth headers.
- **Open-Closed Principle (OCP)**: Adding a new model provider requires zero changes to route handlers or main application code—simply implement the base class and register in the factory.

### 2. Why Server-Sent Events (SSE) over WebSocket?

- **Unidirectional Match**: Large Language Model completions are inherently unidirectional (server pushes tokens sequentially to the client). Full-duplex WebSocket sockets introduce unnecessary state and protocol overhead.
- **Network & Proxy Friendly**: SSE runs over standard HTTP (`HTTP/1.1` or `HTTP/2`), making it work smoothly across CDNs, reverse proxies (Nginx), API gateways, and firewalls without requiring protocol upgrades.
- **Minimal Overhead**: Eliminates WebSocket handshake overhead and comes with standard reconnection support out of the box.

### 3. Why Client-Managed Dialogue Context?

- **Stateless & Scalable**: The server stores no session state or in-memory conversation caches, allowing any instance behind a load balancer to serve any incoming turn.
- **Client Flexibility**: The client can easily implement sliding window pruning, token budget controls, or prompt truncation strategies without touching backend code.

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

We recommend using [uv](https://docs.astral.sh/uv/) for fast setup:

```bash
# Clone the repository
git clone https://github.com/your-username/chat-robot.git
cd chat-robot

# Sync virtual environment and dependencies
uv sync
```

### 2. Environment Configuration

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```ini
# LLM Provider API Keys (configure at least one)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Active Provider (options: deepseek or qwen)
LLM_PROVIDER=deepseek
```

### 3. Run the Development Server

Start the ASGI server with `uv`:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, navigate to:
- 🌐 **Web Chat Demo**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or [http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html)
- 📖 **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Reference

### 1. Health Probe
- **Endpoint**: `GET /health`
- **Response**: `{"status": "ok"}`

### 2. Synchronous Chat
- **Endpoint**: `POST /chat`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "message": "Explain the Factory Pattern in one sentence.",
    "history": [
      { "role": "user", "content": "Hello" },
      { "role": "assistant", "content": "Hi there! How can I assist you today?" }
    ]
  }
  ```
- **Response Body**:
  ```json
  {
    "reply": "The Factory Pattern is a creational design pattern that delegates object instantiation logic to a specialized method or class."
  }
  ```

### 3. Streaming Chat (Server-Sent Events)
- **Endpoint**: `POST /chat/stream`
- **Content-Type**: `application/json`
- **Response Header**: `Content-Type: text/event-stream`
- **cURL Example**:
  ```bash
  curl -N -X POST "http://127.0.0.1:8000/chat/stream" \
    -H "Content-Type: application/json" \
    -d '{
      "message": "Tell a short programmer joke",
      "history": []
    }'
  ```

---

## 📂 Project Structure

```text
chat-robot/
├── app/                          # Core application package
│   ├── __init__.py
│   ├── config.py                 # Configuration loader (.env)
│   ├── main.py                   # FastAPI instance, routes, and middleware
│   ├── models.py                 # Pydantic request & response schemas
│   ├── providers/                # Model providers module
│   │   ├── __init__.py           # get_provider factory method
│   │   ├── base.py               # Abstract base class LLMProvider
│   │   ├── deepseek.py           # DeepSeek implementation
│   │   └── qwen.py               # Alibaba Qwen implementation
│   └── services/                 # Business service logic
│       └── __init__.py
├── docs/                         # Technical docs & ADRs
│   └── architecture.md           # Architecture Decision Records
├── scripts/                      # Experiments, evals & standalone scripts
│   ├── analyze_resume.py         # Structured output/CoT/Pydantic retry demo
│   └── stream_test.py            # Standalone stream validation script
├── static/                       # Static web assets
│   └── index.html                # Built-in chat client WebUI
├── tests/                        # Automated unit & integration tests
│   └── __init__.py
├── .env.example                  # Environment template
├── pyproject.toml                # Project metadata & dependencies
├── uv.lock                       # Exact lockfile
├── LICENSE                       # MIT License
└── README.md                     # Bilingual documentation (English & Chinese)
```

---

## 🧪 Evaluation & Test Scripts

```bash
# Verify real-time token streaming from the active provider
uv run python -m scripts.stream_test

# Run structured resume analysis with schema validation and retry defense
uv run python -m scripts.analyze_resume
```

---

## 🗺️ Roadmap

- [ ] **Conversation Persistence**: Add SQLite / PostgreSQL backing for session history, archiving, and multi-session switching.
- [ ] **Semantic Caching & Rate Limiting**: Integrate Redis to cache frequent LLM queries and provide IP/user-level token throttling.
- [ ] **Authentication & Tenancy**: Add JWT authentication to provide isolated conversation history and user quota management.
- [ ] **Containerization**: Provide minimal multi-stage Dockerfile and `docker-compose.yml` for turnkey deployment.
- [ ] **Automated Testing Suite**: Expand end-to-end test suites using `pytest` and `pytest-asyncio`.

<a id="chinese" name="chinese"></a>

# ChatRobot - 多模型 AI 对话服务框架 (Chinese Version)

<div align="center">

### [🇬🇧 Back to English / 返回顶部英文版](#top) &nbsp; | &nbsp; [🇨🇳 简体中文](#chinese)

[![Python Version](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Package Manager](https://img.shields.io/badge/Package%20Manager-uv-blueviolet?style=flat-square)](https://docs.astral.sh/uv/)
[![Streaming](https://img.shields.io/badge/Streaming-SSE-blue?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

> 💡 **语言切换**：查看英文说明文档？👉 **[点击这里返回顶部英文版 / Return to English version](#top)**。


**ChatRobot** 是一个基于 **FastAPI** 和 **Python 3.12+** 构建的高性能、生产就绪型多模型 AI 对话后端框架。项目采用面向接口与工厂模式设计，原生支持 **DeepSeek**、**通义千问 (Qwen)** 等主流大模型的热插拔切换，提供低延迟打字机级流式传输（SSE）、轻量级无状态多轮对话管理、以及基于 Pydantic 的多重结构化输出防护与容错机制。

---

## 🌟 核心特性

- 🔌 **多 Provider 统一抽象架构**：基于抽象基类（ABC）与工厂模式，隔离厂商 API 差异，支持通过配置无感热插拔切换 Provider。
- ⚡ **打字机级实时流式传输（SSE）**：基于 Server-Sent Events（`text/event-stream`）推送响应，极致缩短首字延迟（TTFT），提供平滑打字机体验。
- 🌐 **无状态轻量设计（Stateless）**：客户端自维护上下文历史（Client-managed Context），服务端无状态，天然具备极高的水平伸缩扩展能力。
- 🛡️ **结构化输出三重防御网**：
  1. *Prompt 级约束*（系统指令 + 格式模板）；
  2. *Schema 运行时强校验*（Pydantic v2 校验与字段清洗）；
  3. *容错自愈与回退重试*（捕获异常并反馈模型二次修正）。
- 🖥️ **内置 WebUI 即开即用**：自带现代化深色交互页面，开箱即验流式打字与多轮对话。
- 🚀 **现代化工程工具链**：使用超高速 Rust 包管理器 `uv` 进行依赖解析与环境隔离，秒级完成构建。

---

## 🛠️ 技术选型

| 维度          | 技术栈                   | 说明                                                        |
| :------------ | :----------------------- | :---------------------------------------------------------- |
| **开发语言**  | Python 3.12+             | 充分利用现代异步协程语法与原生类型标注系统                  |
| **Web 框架**  | FastAPI                  | 现代化高性能异步 ASGI 框架，原生生成 OpenAPI / Swagger 文档 |
| **异步 HTTP** | HTTPX                    | 异步非阻塞通信，支持长连接池、自动重定向与流式响应          |
| **数据建模**  | Pydantic v2              | 工业级强类型数据校验、序列化及异常定位                      |
| **流式推送**  | SSE (Server-Sent Events) | HTTP 标准单向事件流，穿透代理与防火墙，连接轻量稳定         |
| **工程管理**  | uv                       | 极速 Rust 实现的新一代 Python 依赖与环境管理工具            |

---

## 🏛️ 架构设计与设计哲学

> 📘 欲了解详细的设计决策与技术权衡，请阅读：[架构决策记录 (docs/architecture.md)](docs/architecture.md)

### 1. 抽象基类 + 工厂模式

```
                    ┌─────────────────────────┐
                    │     FastAPI 路由层      │
                    │  (/chat, /chat/stream)  │
                    └────────────┬────────────┘
                                 │ 调用
                    ┌────────────▼────────────┐
                    │     get_provider()      │ (工厂函数)
                    └────────────┬────────────┘
                                 │ 依赖抽象 (DIP)
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│        DeepSeekProvider         │   │          QwenProvider           │
│   (继承自抽象基类 LLMProvider)     │   │   (继承自抽象基类 LLMProvider)     │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

- **依赖倒置与解耦**：上层路由仅依赖基类契约，无需知晓具体厂商的请求封装、鉴权 Header 或 Token 解析细节。
- **开闭原则（OCP）**：新增任何第三方模型厂商（如 Claude / GLM / OpenAI），只需继承 `LLMProvider` 并向工厂注册，现有业务代码零改动。

### 2. 为什么流式采用 SSE 而非 WebSocket？

- **场景契合度高**：大语言模型文本补全是典型的一问一答及“服务端向客户端单向推送”场景，无需全双工双向连接。
- **网络穿透友好**：SSE 基于标准 HTTP/1.1 或 HTTP/2，天然兼容 CDN、反向代理（Nginx）、云负载均衡与各类中间件。
- **开销极低**：免去 WebSocket 的握手切换协议（HTTP Upgrade）成本，连接断开后原生支持自动重连。

### 3. 为什么多轮上下文由客户端自维护？

- **高可用与易伸缩**：服务端不维系内存 Session 或分布式锁，任意节点宕机或水平扩容均对请求透明。
- **灵活性**：客户端可自主根据 Token 预算实现历史滑动窗口剪枝（Sliding Window）或消息压缩策略。

---

## 🚀 快速开始

### 1. 克隆代码与依赖安装

建议使用 [uv](https://docs.astral.sh/uv/) 初始化环境并安装依赖：

```bash
# 克隆仓库
git clone https://github.com/your-username/chat-robot.git
cd chat-robot

# 安装并同步项目依赖
uv sync
```

### 2. 配置环境变量

从示例模版创建本地 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件配置模型凭证及默认提供商：

```ini
# 大模型 API Key 配置（至少配置一项）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# 默认使用的模型供应商 (支持: deepseek 或 qwen)
LLM_PROVIDER=deepseek
```

### 3. 运行服务

通过 `uv` 启动本地 ASGI 服务器：

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动完成后，你可以通过浏览器或客户端访问：
- 🌐 **Web 交互界面**：[http://127.0.0.1:8000/](http://127.0.0.1:8000/) 或 [http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html)
- 📖 **Swagger API 交互文档**：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc API 文档**：[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API 接口参考

### 1. 健康检查
- **路径**：`GET /health`
- **说明**：用于负载均衡健康探测及存活探针。
- **响应**：`{"status": "ok"}`

### 2. 同步对话
- **路径**：`POST /chat`
- **Content-Type**：`application/json`
- **请求体**：
  ```json
  {
    "message": "请用一句话解释什么是工厂模式？",
    "history": [
      { "role": "user", "content": "你好" },
      { "role": "assistant", "content": "你好！有什么我可以协助你的？" }
    ]
  }
  ```
- **响应体**：
  ```json
  {
    "reply": "工厂模式是一种创建型设计模式，它提供了一种将对象创建逻辑与具体使用解耦的机制。"
  }
  ```

### 3. 流式对话（Server-Sent Events）
- **路径**：`POST /chat/stream`
- **Content-Type**：`application/json`
- **响应类型**：`text/event-stream`
- **cURL 快速调用示例**：
  ```bash
  curl -N -X POST "http://127.0.0.1:8000/chat/stream" \
    -H "Content-Type: application/json" \
    -d '{
      "message": "讲一个关于程序员的冷笑话",
      "history": []
    }'
  ```

---

## 📂 项目结构

```text
chat-robot/
├── app/                          # 核心业务源码目录
│   ├── __init__.py
│   ├── config.py                 # 环境配置与环境变量加载
│   ├── main.py                   # FastAPI 应用入口、路由与中间件定义
│   ├── models.py                 # Pydantic 请求与响应数据契约 Schema
│   ├── providers/                # 多模型接入抽象与具体实现
│   │   ├── __init__.py           # 工厂方法 get_provider
│   │   ├── base.py               # 抽象基类 LLMProvider
│   │   ├── deepseek.py           # DeepSeek 供应商接入实现
│   │   └── qwen.py               # 通义千问 (Qwen) 供应商接入实现
│   └── services/                 # 业务逻辑服务层（预留会话/业务增强）
│       └── __init__.py
├── docs/                         # 技术决策与设计文档
│   └── architecture.md           # 架构决策记录 (ADR)
├── scripts/                      # 实验、评测与独立验证脚本
│   ├── analyze_resume.py         # 结构化解析/CoT/Pydantic校验与重试演示
│   └── stream_test.py            # Provider 流式功能独立验证脚本
├── static/                       # 静态资源与前端体验页面
│   └── index.html                # 前端打字机对话 WebUI
├── tests/                        # 自动化测试用例
│   └── __init__.py
├── .env.example                  # 环境变量配置示例
├── pyproject.toml                # 项目元数据与依赖定义
├── uv.lock                       # 依赖精确锁定文件
├── LICENSE                       # MIT 开源协议文件
└── README.md                     # 中英双语统一说明文档
```

---

## 🧪 实验与验证脚本

仓库在 `scripts/` 下提供可独立运行的验证脚本：

```bash
# 验证底层 Provider 的流式输出能力
uv run python -m scripts.stream_test

# 运行结构化数据解析与 Pydantic 容错重试机制演示
uv run python -m scripts.analyze_resume
```

---

## 🗺️ 后续路线图 (Roadmap)

- [ ] **多会话持久化支持**：引入 SQLite / PostgreSQL，支持会话列表查询、历史记录恢复与重命名。
- [ ] **分布式缓存与限流**：集成 Redis 实现高频常见问答语义/哈希缓存，以及基于 IP / User 的限流保护。
- [ ] **安全与用户体系**：接入 JWT 身份鉴权机制，实现多租户数据隔离与用量配额。
- [ ] **Docker 容器化**：提供轻量 Alpine/Slim 基础镜像与 `docker-compose.yml` 编排支持。
- [ ] **自动化测试覆盖**：完善基于 `pytest` 与 `pytest-asyncio` 的端到端流式与异常用例覆盖。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。
