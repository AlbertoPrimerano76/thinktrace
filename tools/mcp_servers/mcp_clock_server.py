import asyncio
from datetime import datetime
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server


# Initialize the MCP server
app = Server("time-server", version="1.0.0")


# Register the tool that returns the current time and day of week
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_current_time",
            description="Returns the current time and day of the week",
            inputSchema={"type": "object", "properties": {}},  # No input needed
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_current_time":
        now = datetime.now()
        formatted = now.strftime("Time: %H:%M:%S\nDay: %A")
        return [types.TextContent(type="text", text=formatted)]
    raise ValueError(f"Tool not found: {name}")


# Launch the MCP server using stdio
async def main():
    async with stdio_server() as (reader, writer):
        await app.run(reader, writer, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
