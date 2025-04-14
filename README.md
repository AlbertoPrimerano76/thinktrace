# 🤖 THINKTRACE – Agentic Reasoning & Tool-Aware AI System

> Modular agentic reasoning system for explainable decision-making, with tool-calling via MCP and dynamic LLM planning.

---

## 🧠 Overview

**THINKTRACE** is a production-ready, extensible AI reasoning framework that simulates internal LLM thinking steps, enabling structured reasoning and tool-use through the **MCP (Model Context Protocol)**. It’s powered by [Ollama](https://ollama.com) and optionally extensible with frameworks like **CrewAI**, **Pydantic AI**, or LangGraph.

The system provides:
- Real-time tool invocation when needed (e.g. weather, time).
- JSON-based structured reasoning plans.
- Console or Gradio-based execution & explainability.

---

## 🚀 Features

- ✅ LLM-based structured reasoning with explainable step-by-step logic
- 🛠️ Dynamic external tool integration via MCP servers
- 📊 Rich visualization of reasoning trees (console or UI)
- 📦 Modular architecture: easily extend agents, tools, and frontends
- 📝 YAML-based prompt configuration
- 🔁 Logging: human- and machine-readable outputs

---

## 🧩 How It Works

1. **User input** is parsed into a structured reasoning plan.
2. Reasoning is represented as a sequence of steps (tool use, inference, assumptions).
3. External tools are only invoked when needed (per LLM's internal logic).
4. Final output is built from all steps and displayed with explanation.

🧠 The reasoning logic is defined in `simulation_prompt.yml`.

---

## 🏗️ Project Structure

```
thinktrace/
├── core/
│   ├── config_manager.py        # Loads settings from config/env
│   ├── logger_manager.py        # Centralized Rich logging
│   └── utils.py                 # Utility functions
│
├── components/
│   ├── ollama_interface.py      # Gradio chatbot with tool-calling logic
│   └── prompt_panel.py          # Simulation prompt editor UI
│
├── config/
│   ├── config.py                # Default config definitions
│   ├── mcp_config.json          # Tool server process definitions
│   └── simulation_prompt.yml    # YAML-based reasoning engine prompt
│
├── main.py                      # Gradio + CLI entrypoint
├── requirements.txt             # Dependencies
```

---

## ⚙️ Setup

```bash
# Recommended: use uv for fast dependency management
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## 🧪 Run It

### 🌐 Gradio UI
```bash
python main.py
```

### 🖥️ CLI Mode (Rich Tree Display)
```bash
python main.py --console
```

---

## 🔗 MCP Tool Server Example

The tool server is defined in `mcp_config.json`. You can run a simple clock server using:

```json
{
  "mcpServers": {
    "time-server": {
      "command": "python3",
      "args": ["tools/mcp_servers/mcp_clock_server.py"]
    }
  }
}
```

Add more tools by writing compatible MCP servers and updating this config.

---

## 📤 Output Format

All reasoning paths follow a consistent format like:

```json
{
  "original_question": "What's the time in Tokyo?",
  "intent": "get_time",
  "reasoning_steps": [
    {
      "step_id": 1,
      "step_type": "tool_use",
      "description": "Get time in Tokyo",
      "dependencies": []
    },
    ...
  ],
  "final_output_format": "plain_text"
}
```

---

## 🧩 Prompt Template

You can modify how the agent thinks by editing `simulation_prompt.yml`.

It contains rules like:
- When to use tools
- How to structure the reasoning
- What the final output should look like

---

## 📚 Supported LLMs (tested)

- `llama3.2`
- `mistral-nemo`
- `deepseek-r1:8b`
- `command-r`

Custom models supported via `ollama`.

---

## 💡 Contributing

We welcome contributions of:
- New MCP tools
- Enhanced agents or UIs
- Test cases and bug fixes
- Framework integrations (e.g. LangGraph, LangChain)

Please submit a PR or open an issue!

---

## 👨‍💻 Author

Built with ❤️ by **Alberto Primerano**

---

## 📄 License

MIT License (customize if needed)