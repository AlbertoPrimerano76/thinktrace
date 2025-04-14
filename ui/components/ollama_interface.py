import gradio as gr
from tools import list_models_with_status, run_model, stop_model


def _update_model_table_status(table, model_name, new_status_icon):
    """Update the status column in the table."""
    if not table:
        return []
    for row in table:
        if row[0] == model_name:
            row[3] = new_status_icon
            break
    return table


def _get_model_table():
    """Return the model table with status icons."""
    models = list_models_with_status()
    return [
        [model["name"], model["size"], model["modified"], "🟢 Running" if model["status"] == "running" else "🔴 Stopped"]
        for model in models
    ]


def _make_alert(model_name):
    """Return an HTML alert message for the selected model."""
    if model_name:
        return f"""
        <div style='padding: 10px; background-color: #e6ffed; border-left: 6px solid #22c55e; font-weight: bold; font-family: sans-serif;'>
        ✅ Selected Model: <code>{model_name}</code></div>
        """
    return """
        <div style='padding: 10px; background-color: #fff4f4; border-left: 6px solid #ef4444; font-weight: bold; font-family: sans-serif;'>
        ⚠️ No model selected</div>
    """


def _get_model_options():
    """Return startable and stoppable models."""
    models = list_models_with_status()
    startable = [m["name"] for m in models if m["status"] != "running"]
    stoppable = [m["name"] for m in models if m["status"] == "running"]
    return startable, stoppable, stoppable[:]


def _handle_run(model_name, table, startable, stoppable):
    """Handle model start."""
    if model_name:
        run_model(model_name)
        table = _update_model_table_status(table, model_name, "🟢 Running")
        startable = [m for m in startable if m != model_name]
        if model_name not in stoppable:
            stoppable.append(model_name)

    return (
        table,
        gr.update(choices=startable),
        gr.update(choices=stoppable),
        gr.update(choices=stoppable, value=model_name),
        model_name,
        _make_alert(model_name),
        model_name  # final string value to use externally
    )


def _handle_stop(model_name, table, startable, stoppable):
    """Handle model stop."""
    if model_name:
        stop_model(model_name)
        table = _update_model_table_status(table, model_name, "🔴 Stopped")
        stoppable = [m for m in stoppable if m != model_name]
        if model_name not in startable:
            startable.append(model_name)

    return (
        table,
        gr.update(choices=startable),
        gr.update(choices=stoppable),
        gr.update(choices=stoppable),
        None,
        _make_alert(None),
        ""  # return empty string if no model selected
    )


def _refresh_all():
    """Initial loading of model table and states."""
    table = _get_model_table()
    startable, stoppable, running = _get_model_options()
    default_model = running[0] if running else None
    return (
        table,
        startable,
        stoppable,
        gr.update(choices=startable),
        gr.update(choices=stoppable),
        gr.update(choices=running, value=default_model),
        default_model or "" ,  
        _make_alert(default_model),
        table,
        default_model or "",
        _make_alert(default_model),
    )


def ollama_settings(external_display: gr.Textbox | gr.HTML,selected_model_state: gr.State):
    with gr.Blocks() as interface:
        with gr.Accordion("🧠 Ollama Models", open=False):
            with gr.Row(equal_height=True):
                with gr.Column(scale=1, min_width=300):
                    model_to_run = gr.Dropdown(label="🔼 Start a Model", choices=[], value=None)
                    run_btn = gr.Button("▶️ Launch")

                    model_to_stop = gr.Dropdown(label="🔽 Stop a Model", choices=[], value=None)
                    stop_btn = gr.Button("⏹ Stop")

                    alert = gr.HTML()

                with gr.Column(scale=2):
                    model_table = gr.Dataframe(
                        headers=["Model", "Size", "Last Modified", "Status"],
                        datatype=["str"] * 4,
                        label="📋 Installed Models",
                        interactive=False,
                        row_count=8
                    )

            # States
            table_state = gr.State()
            startable_state = gr.State()
            stoppable_state = gr.State()
            selected_model_value = gr.State()

            # Button actions
            run_btn.click(
                fn=_handle_run,
                inputs=[model_to_run, table_state, startable_state, stoppable_state],
                outputs=[
                    model_table,
                    model_to_run,
                    model_to_stop,
                    model_to_stop,
                    selected_model_state,
                    alert,
                    selected_model_value
                ]
            )

            stop_btn.click(
                fn=_handle_stop,
                inputs=[model_to_stop, table_state, startable_state, stoppable_state],
                outputs=[
                    model_table,
                    model_to_run,
                    model_to_stop,
                    model_to_stop,
                    selected_model_state,
                    alert,
                    selected_model_value
                ]
            )

            selected_model_state.change(
                fn=lambda m: _make_alert(m),
                inputs=selected_model_state,
                outputs=external_display
            )

            # Load models on startup
            interface.load(
                fn=_refresh_all,
                outputs=[
                    model_table,
                    startable_state,
                    stoppable_state,
                    model_to_run,
                    model_to_stop,
                    model_to_stop,
                    selected_model_state,
                    alert,
                    table_state,
                    selected_model_value,
                    external_display
                ]
            )

    return interface, external_display, selected_model_value
