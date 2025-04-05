# 🤖 ThinkTrace

Welcome to the **ThinkTrace** framework — a robust, modular system designed to plug AI tools into agents powered by **Ollama**, **Pydantic AI**, or **CrewAI**, and dynamically reason through tool use with structured, explainable steps.

---

## 🧠 What This Does

This system:
- Wraps any tool (e.g., a weather API, time server, database query, etc.) as an MCP-compatible tool.
- Dynamically suggests and executes tools **only if needed**, using LLM reasoning.
- Supports structured, step-by-step explanation of reasoning logic.
- Supports both console and Gradio chat interfaces.

---

## 🔹 Project Structure

```
core/
├── mcp_client.py          # Generic MCP client to manage tool sessions
├── mcp_server.py          # MCP-compatible tool server lifecycle
├── logger_manager.py      # Rich-powered centralized logging
├── config_manager.py      # Tool and server configuration loader
├── tool_wrapper.py        # Adapter interface for MCP tools

mcp_clients/
├── ollama_reasoning_main.py   # Interactive reasoning engine (Ollama)
├── pydantic_ai_main.py        # Chat interface using Pydantic AI LLMs

mcp_servers/
├── mcp_config.json        # Tool server definitions (cmd, args)
├── mcp_clock_server.py    # Sample time server tool

examples/
├── console_chat_test.py   # Manual reasoning tests

```

---

## 🛠️ Tool Server Configuration

`mcp_servers/mcp_config.json` defines tools like this:

```json
{
  "mcpServers": {
    "time-server": {
      "command": "python3",
      "args": ["mcp_servers/mcp_clock_server.py"]
    }
  }
}
```

---

## 💡 Reasoning Pipeline (Ollama)

Implemented in `ollama_reasoning_main.py`, the LLM agent:

1. **Discovers tool** relevance for the user query.
2. **Generates JSON reasoning** with intent, steps, and logic.
3. **Executes each step** (tool call, inference, formatting).
4. **Explains the full reasoning chain** using `rich.tree`.
5. Supports `Gradio` Chat UI or CLI entry point.

### Run with Gradio
```bash
python ollama_reasoning_main.py  # or gradio ollama_reasoning_main.py
```

---

## 🌐 Reasoning Output Example
For input: `"What's the weather like today in Malaga?"`
```json
{
  "original_question": "What's the weather like today in Malaga?",
  "intent": "weather_inquiry",
  "reasoning_steps": [
    { "step_type": "tool_use", "description": "Call get_current_weather for Malaga" },
    { "step_type": "formatting", "description": "Convert weather result into readable format" }
  ]
}
```

---

## 📈 Model Benchmarking Summary

Tested with `llama3.2`, `mistral-nemo`, `deepseek-r1:8b`, and `command-r`.

| Prompt | Model | Tool Use | Reasoning | Notes |
|--------|--------|----------|-----------|-------|
| What's the weather? | llama3.2 | ✅ Yes | ✅ Detailed | Slight overuse of steps |
| Why do leaves change color? | llama3.2 | ❌ Used tool | ✅ | Should not use tools |
| Say hello in Japanese | mistral-nemo | ❌ Not needed | ✅ | Clean inference |
| Say hello in Japanese | command-r | ❌ Used tool | ✅ | Tool overuse |

---

## 🧪 Pydantic AI Console Chat

Run `pydantic_ai_main.py` to chat using a Pydantic agent backed by your local Ollama model.

```bash
python pydantic_ai_main.py
```

### Includes:
- Token-limited prompt building
- Streaming markdown output with `rich.live`
- Auto cleanup of `MCPClient`

---

## 🚀 Features
- ✅ Modular client/server architecture
- ✅ Gradio + console modes
- ✅ Step-by-step reasoning logic
- ✅ Tool use conditioned on real need
- ✅ Model-agnostic agent (Pydantic, Ollama, etc.)
- ✅ Easy benchmarking of open-source models

---

## 🤧 For Devs: Building New Tool Wrappers
To integrate tools for a new agent type:

```python
async def wrap_tool(session, tool):
    async def wrapper(**kwargs):
        return await session.call_tool(tool.name, arguments=kwargs)

    return {
      "type": "function",
      "function": {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.inputSchema
      }
    }
```

---

## 🚜 For Reload/Live Development
Use Gradio auto-reload:
```bash
gradio ollama_reasoning_main.py  # watches for file changes
```

---

## 🫶 Contributing

Open to improvements, bug reports, and plug-in wrappers for LangGraph, CrewAI, LangChain, etc.

---

Made with ❤️ by Alberto Primerano and the power of open source.

