import asyncio
import shutil
from typing import Any, Callable, Generic, List, TypeVar
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from core import logger

# 🔹 Generic type for tools
ToolType = TypeVar("ToolType")


class MCPServer(Generic[ToolType]):
    """
    🔹 MCPServer: Manages the lifecycle of an individual MCP-compatible server.

    Responsibilities:
    - Start and initialize a subprocess-based tool server.
    - Wrap and expose the tools it provides via a supplied wrapper function.
    - Clean up all resources on shutdown or failure.
    """

    def __init__(
        self,
        name: str,
        config: dict[str, Any],
        tool_wrapper: Callable[[ClientSession, Any], ToolType]
    ) -> None:
        """
        :param name: A unique name for this MCP server instance.
        :param config: Dict containing 'command', 'args', 'env', etc.
        :param tool_wrapper: Function that takes (ClientSession, tool_info) → ToolType
        """
        self.name = name
        self.config = config
        self.tool_wrapper = tool_wrapper
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._cleanup_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        🔹 Initialize the server by launching the subprocess and starting an MCP session.
        """
        try:
            # Resolve executable path
            command = shutil.which("npx") if self.config.get("command") == "npx" else self.config.get("command")
            if not command:
                raise ValueError(f"[{self.name}] Invalid or missing 'command' in server config.")

            # Prepare parameters for starting the server process
            params = StdioServerParameters(
                command=command,
                args=self.config.get("args", []),
                env=self.config.get("env")
            )

            logger.info(f"[{self.name}] 🚀 Launching server: {command} {' '.join(params.args)}")

            # Set up stdio transport and client session
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(params))
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.session = session

            logger.info(f"[{self.name}] ✅ Server initialized and session established.")
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Error during initialization: {e}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize server '{self.name}'") from e

    async def create_tools(self) -> List[ToolType]:
        """
        🔹 Creates and wraps tool instances reported by the server.

        :return: List of tools wrapped with tool_wrapper
        """
        if not self.session:
            raise RuntimeError(f"[{self.name}] Cannot create tools: session is not initialized.")

        try:
            tools_response = await self.session.list_tools()
            tools: List[ToolType] = []

            for tool_info in tools_response.tools:
                wrapped = await self.tool_wrapper(self.session, tool_info)
                tools.append(wrapped)

            logger.info(f"[{self.name}] 🛠️ {len(tools)} tool(s) loaded successfully.")
            return tools
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Failed to create tools: {e}")
            raise RuntimeError(f"Tool creation failed for server '{self.name}'") from e

    async def cleanup(self) -> None:
        """
        🔹 Clean up server subprocess and session resources.
        Always safe to call; protects against multiple invocations.
        """
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                logger.info(f"[{self.name}] 🧹 Server resources cleaned up.")
            except Exception as e:
                logger.error(f"[{self.name}] ⚠️ Error during cleanup: {e}")
