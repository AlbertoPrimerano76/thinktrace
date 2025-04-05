import ollama
from typing import Any
from core import MCPClient, MCPServer, logger

# === Global tool registry ===
tool_impl_global: dict[str, Any] = {}
tools_json_schema_global: list[dict[str, Any]] = []


class OllamaAgent:
    """
    🔹 OllamaAgent integrates with the Ollama client to generate
    responses and optionally call tools defined via MCP servers.
    """

    def __init__(
        self,
        tools: list[dict],
        tool_impl: dict[str, Any],
        model: str = "mistral-nemo"
    ) -> None:
        self.client = ollama.Client()
        self.model = model
        self.tools = tools
        self.tool_impl = tool_impl

    async def run(
        self,
        content: str = None,
        messages: list[dict] = None,
        add_tools: bool = False
    ) -> dict:
        """
        🔹 Run a query through the Ollama model, optionally invoking tools.
        
        :param content: Simple user message to send.
        :param messages: Full message history to send.
        :param add_tools: If True, includes tools in the request.
        :return: Dict with tool, args, and result or answer.
        """
        try:
            logger.info(f"📡 Calling Ollama model '{self.model}'")

            if messages is None:
                if not content:
                    raise ValueError("Either 'content' or 'messages' must be provided.")
                messages = [{"role": "user", "content": content}]

            logger.debug(f"📝 Messages: {[m['content'] for m in messages]}")

            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=self.tools if add_tools else []
            )

            tool_call = response.message.tool_calls[0] if response.message.tool_calls else None

            # Handle tool suggestion
            if tool_call:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                logger.info(f"✅ Tool suggested: {tool_name} | Args: {tool_args}")

                # Skip if any required arg is missing
                if any(not v for v in tool_args.values()):
                    return {
                        "tool": tool_name,
                        "args": tool_args,
                        "result": "Skipped: missing arguments"
                    }

                # Call tool implementation
                tool_fn = self.tool_impl.get(tool_name)
                result = await tool_fn(**tool_args) if callable(tool_fn) else None

                return {
                    "tool": tool_name,
                    "description": "",
                    "args": tool_args,
                    "result": result
                }

            # If no tool was called, return final answer
            return {
                "tool": None,
                "args": {},
                "result": response.message.content.strip()
            }

        except Exception as e:
            logger.exception("❌ Error during Ollama model execution or tool resolution")
            return {
                "tool": None,
                "args": {},
                "result": f"Error: {str(e)}"
            }


# === Wrap MCP tool into Ollama-compatible schema ===
async def _wrap_mcp_tool_as_ollama_tools(session, tool) -> dict:
    """
    Convert an MCP tool to Ollama-compatible tool schema and register its executor.
    """
    async def async_wrapper(**kwargs):
        return await session.call_tool(tool.name, arguments=kwargs)

    # Register tool
    tool_impl_global[tool.name] = async_wrapper

    schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    }

    tools_json_schema_global.append(schema)
    return schema


# === Construct agent and tool client ===
async def get_ollama_ai_agent(llm_model: str = "mistral-nemo") -> tuple[MCPClient, OllamaAgent]:
    """
    Load tools from MCP servers and return an initialized OllamaAgent.

    :param llm_model: The name of the Ollama model to use.
    :return: A tuple of (MCPClient, OllamaAgent)
    """
    client = MCPClient(
        server_class=MCPServer,
        tool_wrapper=_wrap_mcp_tool_as_ollama_tools
    )
    client.load_servers()
    tools = await client.start()
    agent = OllamaAgent(tools=tools, tool_impl=tool_impl_global, model=llm_model)

    return client, agent
