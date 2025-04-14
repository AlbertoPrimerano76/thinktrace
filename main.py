import gradio as gr
from ui import ollama_settings, prompt_settings,chat_handler,debug_output
with gr.Blocks() as demo:
    gr.HTML("""
        <style>
        .debug-step {
            margin-bottom: 14px;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 8px;
            background-color: #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .debug-summary {
            font-size: 17px;
            font-weight: 600;
            cursor: pointer;
            padding: 8px;
            margin: 0;
            border-radius: 8px;
        }

        .debug-code {
            background-color: #f4f4f4;
            color: #333;
            padding: 12px;
            margin-top: 6px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 14px;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        .intent-step    { color: #1565c0; }
        .generation-step{ color: #2e7d32; }
        .final-step     { color: #ef6c00; }
        .error-step     { color: #c62828; }
        .default-step   { color: #333; }
        </style>
        """)


    selected_model_state = gr.State()
    gr.Markdown("# 🧠 ThinkTrace Control Panel")
    with gr.Tab("Chat ..."):
        selected_model_display = gr.HTML()
        with gr.Accordion("📐 Fine-Tune Model Output", open=False):
             with gr.Row():
                top_k = gr.Slider(0.0,100.0, label="top_k", value=40, info="Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative. (Default: 40)")
                top_p = gr.Slider(0.0,1.0, label="top_p", value=0.9, info=" Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. (Default: 0.9)")
                temp = gr.Slider(0.0,2.0, label="temperature", value=0.8, info="The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)")
        
        chatbot_ui = gr.ChatInterface(
            fn=chat_handler,
            chatbot=gr.Chatbot(type="messages"),
            type="messages",
            additional_inputs=[
                selected_model_state,
                top_k,top_p,temp,
            ],
            additional_outputs=[debug_output],
            additional_inputs_accordion=None
        )        
        
    with gr.Tab("AI Settings..."):
        ollama_panel, selected_model_display, selected_model_state = ollama_settings(selected_model_display,selected_model_state)
        system_prompt = prompt_settings()
    with gr.Tab("Debug"):
        with gr.Accordion("🧩 Reasoning Steps", open=True):
            debug_output.render()
        
demo.queue().launch(debug=True)
