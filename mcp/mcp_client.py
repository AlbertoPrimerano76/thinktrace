import json
from typing import Any, List, Callable, Generic, Type
from contextlib import AsyncExitStack
from pathlib import Path
from core import logger
from core import config_manager, SCRIPT_DIR
from .mcp_server import MCPServer, ToolType

class MCPClient(Generic[ToolType]):
    """
    🔹 Generic MCPClient for managing multiple MCPServer instances.
    
    Responsibilities:
    - Load configuration from JSON.
    - Create and initialize each MCPServer.
    - Aggregate and expose all tool instances.
    - Handle cleanup of all resources.
    """

    def __init__(
        self,
        server_class: Type[MCPServer[ToolType]],
        tool_wrapper: Callable[[Any, Any], ToolType]
    ) -> None:
        """
        :param server_class: Class reference to your MCPServer implementation.
        :param tool_wrapper: Function to wrap a tool definition (e.g. schema, method).
        """
        self.server_class = server_class
        self.tool_wrapper = tool_wrapper
        self.servers: List[MCPServer[ToolType]] = []
        self.config: dict[str, Any] = {}
        self.exit_stack = AsyncExitStack()

    def load_servers(self) -> None:
        """
        Load MCP server definitions from a JSON config file.
        Populates `self.servers` with server instances.
        """
        config_path: Path = SCRIPT_DIR / "mcp_servers" / config_manager.MCP_CONFIG_FILE_NAME

        if not config_path.exists():
            logger.error(f"❌ Configuration file not found: {config_path}")
            raise FileNotFoundError(f"MCP config file not found at: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                self.config = json.load(config_file)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in configuration file: {e}")
            raise ValueError("Failed to parse MCP configuration file.") from e

        if "mcpServers" not in self.config:
            logger.error("❌ Missing 'mcpServers' key in configuration.")
            raise ValueError("Invalid configuration: 'mcpServers' section is required.")

        self.servers = [
            self.server_class(name, cfg, self.tool_wrapper)
            for name, cfg in self.config["mcpServers"].items()
        ]
        logger.info(f"✅ Loaded {len(self.servers)} MCP server(s) from config.")

    async def start(self) -> List[ToolType]:
        """
        Start all loaded MCP servers and return a combined list of their tools.
        
        :return: List of tools across all initialized servers.
        """
        all_tools: List[ToolType] = []

        for server in self.servers:
            try:
                await server.initialize()
                tools = await server.create_tools()
                all_tools.extend(tools)
            except Exception as e:
                logger.error(f"❌ Failed to start server '{server.name}': {e}")
                await self.cleanup()
                return []

        logger.info(f"✅ Started {len(self.servers)} server(s), loaded {len(all_tools)} tool(s).")
        return all_tools

    async def cleanup(self) -> None:
        """
        Clean up all server resources and exit stack.
        Called automatically in failure scenarios or at shutdown.
        """
        for server in self.servers:
            try:
                await server.cleanup()
            except Exception as e:
                logger.warning(f"⚠️ Cleanup failed for server '{server.name}': {e}")

        await self.exit_stack.aclose()
        logger.info("🧹 All MCPClient resources cleaned up.")
