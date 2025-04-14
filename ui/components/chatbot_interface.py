import json
import html
import gradio as gr
from core import logger
from tools import run_reasoning_pipeline, get_ollama_ai_agent

# 🔹 Load the Ollama-based MCP agent
async def load_agent(selected_model):
    try:
        return await get_ollama_ai_agent(selected_model)
    except Exception as e:
        logger.exception("Failed to load Ollama agent")
        raise RuntimeError("Could not initialize the AI agent.") from e


def format_debug_markdown(debug_info: dict) -> str:
    step = debug_info.get("step", "–")
    title = debug_info.get("title", "")
    emoji = debug_info.get("emoji", "")
    css_class = debug_info.get("css_class", "")
    cleaned_info = {k: v for k, v in debug_info.items() if k not in ["step", "title"]}

    # Escape & format JSON nicely
    inner = html.escape(json.dumps(cleaned_info, indent=2))

    return f"""
        <details class="debug-step" open>
        <summary class="{css_class}">{emoji} Step {step} — {title}</summary>
        <pre><code>{inner}</code></pre>
        </details>
    """


def format_debug_html(debug_info: dict, open_by_default=True) -> str:
    step = debug_info.get("step", "–")
    title = debug_info.get("title", "")
    emoji = debug_info.get("emoji", "")
    css_class = debug_info.get("css_class", "")
    open_tag = "open" if open_by_default else ""
    
    cleaned_info = {k: v for k, v in debug_info.items() if k not in ["step", "title"]}
    inner = html.escape(json.dumps(cleaned_info, indent=2))

  

    return f"""
        <details class="debug-step" {open_tag}>
        <summary class="debug-summary {css_class}">{emoji} <strong>Step {step} — {title}</strong></summary>
        <pre class="debug-code"><code>{inner}</code></pre>
        </details>
    """



debug_output = gr.HTML()

async def chat_handler(message: str, history: list, llm_model, top_k: float, top_p: float, temperature: float):
    """
    Streams assistant response step-by-step AND updates debug output in real-time.
    Displays one chatbot message per reasoning step.
    """
    debug_lines = []

    if not llm_model:
        yield [{"role": "assistant", "content": "⚠️ Please select a model first."}], ""
        return

    # Clear debug output at the beginning
    yield [], ""
    try:
        ollama_client, ollama_agent = await load_agent(llm_model)

        # Step-by-step reasoning
        async for result in run_reasoning_pipeline(
            user_question=message,
            llm_agent=ollama_agent,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature
        ):
            # Get current reasoning info
            chat_msg = result.get("chat", "...")
            debug_info = result.get("debug", {})

            # Format debug info
            formatted_debug = format_debug_html(debug_info)
            debug_lines.append(formatted_debug)
            chat_msg = chat_msg.replace("\n", "<br>")

            #  Append single message to chat history (one per step)
            yield [{"role": "assistant", "content": chat_msg}], "\n\n\n".join(debug_lines)

    finally:
        logger.debug("Pipeline execution completed.")
        try:
            await ollama_client.cleanup()
        except Exception as e:
            logger.warning(f"🧹 Cleanup failed: {e}")