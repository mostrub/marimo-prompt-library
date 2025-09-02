import marimo

__generated_with = "0.8.18"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    from src.marimo_notebook.modules import cli_llm_module, prompt_library_module
    return cli_llm_module, mo, prompt_library_module


@app.cell
def __(cli_llm_module, mo):
    # Build CLI models
    cli_models = cli_llm_module.build_cli_models()

    # Select which models to use
    active_models = {
        "gemini-cli": cli_models["gemini-cli"],
        "gemini-flash-cli": cli_models["gemini-flash-cli"],
        "gemini-pro-cli": cli_models["gemini-pro-cli"],
    }

    mo.md(f"**Available CLI Models:** {', '.join(active_models.keys())}")
    return active_models, cli_models


@app.cell
def __():
    prompt_styles = {"background": "#eee", "padding": "10px", "border-radius": "10px"}
    return (prompt_styles,)


@app.cell
def __(active_models, mo):
    # Create UI components
    prompt_input = mo.ui.text_area(
        label="Enter your prompt:",
        value="Write a haiku about coding",
        full_width=True
    )

    model_dropdown = mo.ui.dropdown(
        options=list(active_models.keys()),
        label="Select Model",
        value="gemini-cli"
    )

    run_button = mo.ui.button(label="Run Prompt", kind="success")

    form = (
        mo.md(
            r"""
            # CLI Model Prompting (Gemini CLI)

            This notebook uses Gemini CLI directly from your terminal.

            {prompt_input}

            {model_dropdown}

            {run_button}
            """
        )
        .batch(
            prompt_input=prompt_input,
            model_dropdown=model_dropdown,
            run_button=run_button
        )
        .form()
    )
    form
    return form, model_dropdown, prompt_input, run_button


@app.cell
def __(active_models, cli_llm_module, form, mo, prompt_styles):
    if form.value and form.value["run_button"]:
        selected_model = active_models[form.value["model_dropdown"]]
        prompt_text = form.value["prompt_input"]

        mo.md(f"**Running prompt with {form.value['model_dropdown']}...**")

        # Run the prompt
        response = cli_llm_module.prompt_with_cli(selected_model, prompt_text)

        # Display results
        mo.vstack([
            mo.md("### Prompt:"),
            mo.md(f"```\n{prompt_text}\n```").style(prompt_styles),
            mo.md("### Response:"),
            mo.md(f"```\n{response}\n```").style(prompt_styles)
        ])
    else:
        mo.md("*Enter a prompt and click 'Run Prompt' to get started*")
    return prompt_text, response, selected_model


@app.cell
def __(mo, prompt_library_module):
    # Load testable prompts for quick access
    testable_prompts = prompt_library_module.pull_in_testable_prompts()
    if testable_prompts:
        mo.md("### Quick Access to Test Prompts")
        
        # Create a simple accordion using mo.ui.accordion with correct API
        accordion_dict = {
            "Sample Category (3 prompts)": mo.md("Sample prompt content here...")
        }
        
        mo.ui.accordion(accordion_dict)
    else:
        mo.md("No testable prompts found.")
    return accordion_dict, testable_prompts


if __name__ == "__main__":
    app.run()
