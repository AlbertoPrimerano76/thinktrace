from core import logger, show_reasoning_tree
from tools import execute_reasoning, generate_reasoning_json, load_agent


async def gradio_chain(message, history):
    try:
        mcp_client, agent = await load_agent()
        reasoning = generate_reasoning_json(message)
        if not reasoning:
            return "❌ Could not generate reasoning."
        
        show_reasoning_tree(reasoning)
        answer = await execute_reasoning(agent, reasoning, show_progress=False)
        return answer
    except Exception as e:
        logger.exception("Error during Gradio chain")
        return f"⚠️ Error: {e}"
    finally:
        if 'mcp_client' in locals():
            await mcp_client.cleanup()
            logger.info("🧹 MCP client cleanup complete")
