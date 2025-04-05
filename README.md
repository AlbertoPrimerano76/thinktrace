
🤖 THINKTRACE – Agentic Reasoning & Tool-Aware AI System
========================================================

Welcome to **ThinkTrace**, a modular and production-grade framework that integrates AI tools into LLM agents
via the MCP protocol, powered by **Ollama**, and optionally extendable with **CrewAI**, **Pydantic AI**, or other agent frameworks.

ThinkTrace enables tool-aware reasoning through structured steps, decision trees, and explainable outputs,
accessible via both console and UI interfaces.

--------------------------------------------------
🧠 WHAT THIS DOES
--------------------------------------------------
- Wraps any tool (weather API, time server, etc.) as an MCP-compatible function.
- Dynamically suggests and invokes tools only when needed using LLM reasoning.
- Generates structured JSON reasoning trees.
- Executes reasoning paths and explains steps via console (`rich.tree`) or Gradio chat.
- Logs everything in human-readable and machine-readable formats.

--------------------------------------------------
📂 PROJECT STRUCTURE
--------------------------------------------------
thinktrace/
├── core/
│   ├── config_manager.py      -> Loads and validates .env settings
│   ├── logger_manager.py      -> Rich-based logging and rotating file logs
│   ├── tree_renderer.py       -> Renders beautiful reasoning trees
│   └── mcp_server.py          -> Manages lifecycle of subprocess-based tools
│
├── tools/
│   └── reasoning_engine.py    -> Main logic for LLM planning & step execution
│
├── ui/
│   └── ui_gradio.py           -> Chat UI with step-by-step reasoning
│
├── ai/
│   └── ollama_agent.py        -> Ollama-based tool-aware agent
│
├── main.py                    -> CLI or Gradio entry point
├── .env                       -> Environment variables
├── requirements.txt           -> Pip dependencies (use with `uv pip install`)
├── mcp_servers/
│   ├── mcp_config.json        -> Tool server definitions
│   └── mcp_clock_server.py    -> Example: tool to get current time

--------------------------------------------------
⚙️ SETUP INSTRUCTIONS (with uv)
--------------------------------------------------
$ uv venv
$ source .venv/bin/activate
$ uv pip install -r requirements.txt

--------------------------------------------------
🛠️ TOOL SERVER CONFIGURATION (mcp_config.json)
--------------------------------------------------
{
  "mcpServers": {
    "clock-server": {
      "command": "python3",
      "args": ["mcp_servers/mcp_clock_server.py"]
    }
  }
}

--------------------------------------------------
💡 REASONING PIPELINE
--------------------------------------------------
1. Agent parses the user question
2. Agent generates structured JSON with intent & steps
3. Tool usage is conditionally suggested
4. Each step is executed (tool or inference)
5. Final answer is returned and explained

--------------------------------------------------
🖼️ REASONING EXAMPLE (JSON)
--------------------------------------------------
Input: "What's the time in Tokyo?"

{
  "original_question": "What's the time in Tokyo?",
  "intent": "get_time",
  "reasoning_steps": [
    {
      "step_type": "tool_use",
      "description": "Call get_current_time for Tokyo"
    },
    {
      "step_type": "formatting",
      "description": "Format time result into readable output"
    }
  ]
}

--------------------------------------------------
✅ FEATURES
--------------------------------------------------
- Reasoning tree displayed in console or Gradio
- File + terminal logs
- Tool execution control (skip if missing args)
- MCP client auto-loading and cleanup
- Language model agnostic
- Modular architecture

--------------------------------------------------
🧪 SUPPORTED MODELS (benchmarked)
--------------------------------------------------
- llama3.2
- mistral-nemo
- deepseek-r1:8b
- command-r

--------------------------------------------------
🔧 TOOL WRAPPER TEMPLATE
--------------------------------------------------
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

--------------------------------------------------
🚀 DEVELOPMENT
--------------------------------------------------
Live dev with Gradio:
$ gradio thinktrace/main.py

Run CLI:
$ python thinktrace/main.py

--------------------------------------------------
🫶 CONTRIBUTING
--------------------------------------------------
We welcome:
- New MCP tools and wrappers
- Feedback or feature requests
- Integrations with LangGraph, CrewAI, LangChain

Built with ❤️ by Alberto Primerano
