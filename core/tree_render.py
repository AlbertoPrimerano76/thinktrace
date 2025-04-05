import json
from rich.tree import Tree
from rich.console import Console

console = Console()


def show_reasoning_tree(reasoning: dict):
    console.rule("[bold cyan]🧠 Reasoning Tree")
    tree = Tree(
        f"📌 Question: [bold]{reasoning.get('original_question', 'N/A')}[/bold]"
    )

    intent = reasoning.get("intent", "N/A")
    if isinstance(intent, dict):
        intent = f"{intent.get('intent_name', '')} (confidence: {intent.get('confidence', 'N/A')})"
    tree.add(f"🎯 Intent: {intent}")

    steps_branch = tree.add("🧩 Reasoning Steps")
    for step in reasoning.get("reasoning_steps", []):
        step_node = steps_branch.add(
            f"[bold]{step['step_id']}[/bold] ({step['step_type']}): {step['description']}"
        )
        if step.get("question"):
            step_node.add(f"❓ Question: {step['question']}")
        if step.get("dependencies"):
            step_node.add(f"🔗 Depends on: {', '.join(map(str, step['dependencies']))}")
        if step.get("known_facts"):
            step_node.add(f"📚 Known facts: {', '.join(step['known_facts'])}")
        if step.get("inferred_facts"):
            step_node.add(f"🧠 Inferred facts: {', '.join(step['inferred_facts'])}")

    tree.add(
        f"📝 Required Info: {json.dumps(reasoning.get('required_info', {}), indent=2)}"
    )
    tree.add(f"📦 Output Format: {reasoning.get('final_output_format', 'N/A')}")
    tree.add(f"🗒️ Notes: {reasoning.get('notes', 'None')}")

    console.print(tree)


def show_execution_tree(tree: Tree):
    console.rule("[bold magenta]🔁 Reasoning Execution")
    console.print(tree)


def show_final_answer(answer: str):
    console.rule("[bold green]✅ Final Answer")
    console.print(f"[bold green]{answer}[/bold green]")
