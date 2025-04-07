import asyncio
import gradio as gr
from ui import gradio_chain

# Define the demo globally so gradio's reloader can access it
demo = gr.ChatInterface(fn=lambda msg, hist: asyncio.run(gradio_chain(msg, hist)))

def launch_app():
    demo.launch()

if __name__ == "__main__":
    launch_app()
