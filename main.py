import asyncio
import gradio as gr
from ui import gradio_chain

def launch_app():
    demo = gr.ChatInterface(fn=lambda msg, hist: asyncio.run(gradio_chain(msg, hist)))
    demo.launch()

if __name__ == "__main__":
    launch_app()
