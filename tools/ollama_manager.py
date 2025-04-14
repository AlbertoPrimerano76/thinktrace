import subprocess
import re
from typing import List, Dict

def run_command(cmd: str) -> str:
    """
    Executes a shell command and returns its stdout as a string.
    Captures stderr and returns a formatted error message on failure.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return f"❌ Error executing '{cmd}': {error_msg}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def parse_installed_models(raw_output: str) -> List[Dict[str, str]]:
    """
    Parses the output of 'ollama ls' to extract installed model details.

    Expected format (example):
    NAME         TAG       SIZE    MODIFIED
    llama3       latest    4.2GB   2024-04-08

    Returns:
        A list of models with name, size, modified date, and status.
    """
    lines = raw_output.strip().split("\n")
    models = []
    
    if len(lines) < 2:
        return models  # No models found

    for line in lines[1:]:  # Skip header
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 4:
            models.append({
                "name": parts[0],
                "size": parts[2],
                "modified": parts[3],
                "status": "stopped"
            })
    return models

def parse_running_models(raw_output: str) -> List[str]:
    """
    Parses the output of 'ollama ps' to extract the names of running models.

    Expected format:
    NAME         STATUS
    llama3       running

    Returns:
        A list of model names that are currently running.
    """
    lines = raw_output.strip().split("\n")
    running_models = []

    if len(lines) < 2:
        return running_models  # No running models

    for line in lines[1:]:  # Skip header
        parts = re.split(r"\s{2,}", line.strip())
        if parts:
            running_models.append(parts[0])
    return running_models

def list_models_with_status() -> List[Dict[str, str]]:
    """
    Combines installed and running model information to produce a status list.

    Returns:
        A list of all installed models, with their current status ('running' or 'stopped').
    """
    raw_installed = run_command("ollama ls")
    raw_running = run_command("ollama ps")

    # Handle command errors
    if raw_installed.startswith("❌") or raw_running.startswith("❌"):
        return [{"error": raw_installed if raw_installed.startswith("❌") else raw_running}]
    
    installed_models = parse_installed_models(raw_installed)
    running_models = parse_running_models(raw_running)

    # Match installed models with running models
    for model in installed_models:
        if model["name"] in running_models:
            model["status"] = "running"
    return installed_models

def run_model(model_name: str) -> str:
    """
    Runs the specified Ollama model.
    
    Args:
        model_name: The name of the model to run.

    Returns:
        A message indicating success or failure.
    """
    if not model_name:
        return "⚠️ Please provide a model name to run."
    return run_command(f"ollama run {model_name}")

def stop_model(model_name: str) -> str:
    """
    Stops the specified Ollama model.
    
    Args:
        model_name: The name of the model to stop.

    Returns:
        A message indicating success or failure.
    """
    if not model_name:
        return "⚠️ Please provide a model name to stop."
    return run_command(f"ollama stop {model_name}")
