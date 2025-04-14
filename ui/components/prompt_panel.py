# ui/prompt_panel.py

import gradio as gr
from core import config_manager,load_simulation_prompt  # Adjust import path to match your structure

def prompt_settings():
    # Load the prompt text from YAML
    try:
        path = config_manager.CONFIG_FOLDER_PATH +"/"+config_manager.PROMPT_FILE_NAME
        prompt_text = load_simulation_prompt(path)
    except Exception as e:
        prompt_text = f"❌ Failed to load prompt: {str(e)}"

    with gr.Blocks() as reasoning_prompt:
        with gr.Accordion("📝 Prompts", open=False):
            gr.Textbox(
                label="Reasoning Prompt",
                value=prompt_text,
                lines=20,
                interactive=True,  # Set to False if you want it read-only
                show_copy_button=True
            )
    return reasoning_prompt
