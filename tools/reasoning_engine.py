import re
import json
import ollama
from datetime import datetime, timezone
from rich.tree import Tree
from rich.progress import Progress

from core import logger,config_manager,show_execution_tree,show_final_answer
from mcp import get_ollama_ai_agent


MODEL_NAME = config_manager.MODEL_NAME
ENABLE_TREE_DISPLAY = config_manager.ENABLE_TREE_DISPLAY

# Initialize Ollama client
client = ollama.Client()


# 🔹 Load the Ollama-based MCP agent
async def load_agent():
    try:
        return await get_ollama_ai_agent(MODEL_NAME)
    except Exception as e:
        logger.exception("Failed to load Ollama agent")
        raise RuntimeError("Could not initialize the AI agent.") from e


# 🔹 Parse JSON output from LLM reasoning response
def extract_json_from_response(content: str) -> dict:
    # Extract JSON block from triple-backtick code block
    match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL) or \
            re.search(r"```(.*?)```", content, re.DOTALL)
    if match:
        content = match.group(1).strip()
    try:
        data = json.loads(content)
        # Fix common key typo if needed
        for step in data.get("reasoning_steps", []):
            if "infferred_facts" in step:
                step["inferred_facts"] = step.pop("infferred_facts")
        return data
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {}


# 🔹 Prompt Ollama to generate a reasoning breakdown for a user question
def generate_reasoning_json(question: str) -> dict:
    simulation_prompt = f"""
You are a reasoning engine simulating the internal decision-making of a language model.
Your task is to decompose this question into a structured reasoning path:

🔹 Only use a tool if real-time info is needed.
🔹 Use your own knowledge otherwise.

Question:
{question}
"""

    messages = [
        {"role": "system", "content": "You simulate LLM reasoning steps."},
        {"role": "user", "content": simulation_prompt}
    ]

    try:
        response = client.chat(model=MODEL_NAME, messages=messages)
        return extract_json_from_response(response.message.content.strip())
    except Exception as e:
        logger.exception(f"Failed to generate reasoning JSON: {e}")
        return {}


# 🔹 Execute the reasoning plan: resolve tool calls, infer steps, track output
async def execute_reasoning(agent, reasoning: dict, show_progress: bool = False) -> str:
    steps_result = {}  # Map of step_id to resolved value
    tree = Tree(f"🤖 [bold]Execution: {reasoning.get('original_question', '')}[/bold]")
    steps = reasoning.get("reasoning_steps", [])
    progress = Progress() if show_progress else None
    task = None

    if show_progress:
        progress.start()
        task = progress.add_task("Processing steps...", total=len(steps))

    for step in steps:
        step_id = step["step_id"]
        node = tree.add(f"[bold]{step_id}[/bold] ({step['step_type']}): {step['description']}")

        # Collect known facts and resolved dependencies
        deps = step.get("dependencies", [])
        known_facts = step.get("known_facts", []) + [steps_result.get(dep, "") for dep in deps]

        # Resolve tool_use or inference steps
        if step["step_type"] == "tool_use":
            try:
                result = await agent.run(content=step.get("question"), add_tools=True)
                tool_name = result.get("tool")
                steps_result[step_id] = result.get("result", "Skipped")
                node.add(f"🛠️ Tool: {tool_name} -> [green]{steps_result[step_id]}[/green]")
            except Exception as e:
                logger.warning(f"Tool execution failed: {e}")
                steps_result[step_id] = "Error"
        else:
            # Inference step: just aggregate known and inferred facts
            steps_result[step_id] = ", ".join(known_facts + step.get("inferred_facts", []))
            node.add(f"🧠 Inferred: {steps_result[step_id]}")

        if show_progress:
            progress.advance(task)

    if show_progress:
        progress.stop()

    # Show execution tree in console if enabled
    if ENABLE_TREE_DISPLAY:
        show_execution_tree(tree)

    # Generate final answer based on the last resolved step
    final_prompt = f"Generate an answer to: '{reasoning.get('original_question')}' using: '{steps_result.get(steps[-1]['step_id'], '')}'"
    try:
        final_response = client.chat(model=MODEL_NAME, messages=[
            {"role": "system", "content": "You finalize the answer."},
            {"role": "user", "content": final_prompt}
        ])
        final_answer = final_response.message.content.strip()

        if ENABLE_TREE_DISPLAY:
            show_final_answer(final_answer)

        # Log structured outcome
        log_run(reasoning, steps_result, final_answer)

        return final_answer
    except Exception as e:
        logger.exception(f"Failed to generate final response: {e}")
        return "⚠️ Failed to generate final answer."


# 🔹 Log the reasoning session (structured JSON in a single log line)
def log_run(reasoning, steps_result, final_answer):
    try:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL_NAME,
            "agent": "ollama",
            "question": reasoning.get("original_question"),
            "intent": reasoning.get("intent"),
            "steps": reasoning.get("reasoning_steps"),
            "final_output_format": reasoning.get("final_output_format"),
            "notes": reasoning.get("notes"),
            "results": steps_result,
            "final_answer": final_answer
        }
        logger.info(json.dumps(log_entry, ensure_ascii=False))
    except Exception as e:
        logger.warning(f"Could not serialize log entry: {e}")
