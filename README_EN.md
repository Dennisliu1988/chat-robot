# ChatRobot - Multi-Provider LLM Dialogue Service Framework

<p align="center">
  <a href="README.md"><b>🇨🇳 简体中文</b></a> | <a href="README_EN.md"><b>🇬🇧 English</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic" />
  <img src="https://img.shields.io/badge/Package%20Manager-uv-blueviolet?style=flat-square" alt="uv" />
  <img src="https://img.shields.io/badge/Streaming-SSE-blue?style=flat-square" alt="SSE" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

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

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Leverages modern `async`/`await` primitives and strict type annotations |
| **Web Framework** | FastAPI | High-performance ASGI framework with automatic OpenAPI / Swagger generation |
| **HTTP Client** | HTTPX | Fully asynchronous, non-blocking HTTP client supporting connection pools and streaming |
| **Data Validation** | Pydantic v2 | Industry-standard schema validation, serialization, and error tracing |
| **Streaming Protocol**| SSE (Server-Sent Events) | Native HTTP unidirectional event stream, lightweight and firewall/proxy friendly |
| **Package Manager**| uv | Blazing fast Python package manager written in Rust |

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
- **Description**: Lightweight health check for liveness/readiness probes.
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
- **Stream Output**:
  ```text
  data: Why
  data:  do
  data:  programmers
  data:  wear
  data:  glasses?
  data:  Because they
  data:  cannot C#!
  data: [DONE]
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
│   └── services/                 # Business service logic (reserved for extensions)
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
├── README.md                     # Chinese documentation
└── README_EN.md                  # English documentation
```

---

## 🧪 Evaluation & Test Scripts

Run the standalone exploration scripts under `scripts/`:

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

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
