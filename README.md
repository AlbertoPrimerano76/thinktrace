# 🤖 ThinkTrace MCP Agentic Framework

Welcome to the **ThinkTrace Modular Agentic Reasoning System**, a powerful AI infrastructure for **structured reasoning**, **dynamic tool use**, and **explainable LLM-based workflows** using **Ollama**, **MCP**, and optionally **Gradio** for UI.

Built for speed, transparency, and modularity.

---

## 🧠 What It Does

- Dynamically **suggests and invokes tools only when necessary**.
- Produces **structured reasoning steps** (intent, dependencies, final output).
- Explains each step via **Rich console tree** or **Gradio chat**.
- Wraps **MCP-compatible tools** into Ollama/LLM agents.
- Easily extended with Pydantic, CrewAI, or LangGraph agents.

---

## 🗂️ Project Structure

thinktrace/ ├── core/ │ ├── config_manager.py # Loads settings from .env │ ├── logger_manager.py # Rich-based logging (console + file) │ ├── tree_renderer.py # Pretty tree output for reasoning steps │ └── mcp_server.py # Server-side lifecycle │ ├── tools/ │ └── reasoning_engine.py # LLM reasoning + step execution (Ollama) │ ├── ui/ │ └── ui_gradio.py # Gradio-based chat frontend │ ├── ai/ │ └── ollama_agent.py # Ollama agent + tool resolver │ ├── main.py # Gradio/CLI entry point ├── .env # Environment variables ├── requirements.txt


---

## ⚙️ Setup & Activation (using [uv](https://github.com/astral-sh/uv))

