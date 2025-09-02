import marimo

__generated_with = "0.8.18"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    from src.marimo_notebook.modules import prompt_library_module, llm_module, cli_llm_module
    import re  # For regex to extract placeholders
    return cli_llm_module, llm_module, mo, prompt_library_module, re


@app.cell
def __(prompt_library_module):
    map_prompt_library: dict = prompt_library_module.pull_in_prompt_library()
    testable_prompts: dict = prompt_library_module.pull_in_testable_prompts()
    
    # Combine both prompt libraries
    all_prompts = {}
    
    # Add prompt library prompts with "library/" prefix
    for key, value in map_prompt_library.items():
        all_prompts[f"library/{key}"] = value
    
    # Add testable prompts with "testable/" prefix
    for key, value in testable_prompts.items():
        all_prompts[f"testable/{key}"] = value
    
    return all_prompts, map_prompt_library, testable_prompts


@app.cell
def __(cli_llm_module, llm_module):
    # Build CLI models
    cli_models = cli_llm_module.build_cli_models()
    
    # Try to build API models (will only work if API keys are set)
    api_models = {}
    try:
        gemini_1_5_pro, gemini_1_5_flash = llm_module.build_gemini_duo()
        api_models["gemini-1-5-pro-api"] = gemini_1_5_pro
        api_models["gemini-1-5-flash-api"] = gemini_1_5_flash
    except:
        pass
    
    # Combine all models
    models = {
        "gemini-cli": cli_models["gemini-cli"],
        "gemini-flash-cli": cli_models["gemini-flash-cli"],
        "gemini-pro-cli": cli_models["gemini-pro-cli"],
    }
    
    # Add API models if available
    models.update(api_models)
    
    return api_models, cli_models, gemini_1_5_flash, gemini_1_5_pro, models


@app.cell
def __():
    prompt_styles = {"background": "#eee", "padding": "10px", "border-radius": "10px"}
    return prompt_styles,


@app.cell
def __(all_prompts, mo, models):
    # Sort prompt keys for better organization
    sorted_prompt_keys = sorted(all_prompts.keys())
    
    # Group by category
    categorized_prompts = {}
    for key in sorted_prompt_keys:
        parts = key.split('/')
        category = parts[1] if len(parts) > 2 else parts[0]
        if category not in categorized_prompts:
            categorized_prompts[category] = []
        categorized_prompts[category].append(key)
    
    # Create options for dropdown with categories
    prompt_options = []
    for category, prompts in sorted(categorized_prompts.items()):
        for prompt_key in prompts:
            display_name = prompt_key.replace('testable/', '').replace('library/', '')
            prompt_options.append({
                "label": f"[{category}] {display_name.split('/')[-1]}",
                "value": prompt_key
            })
    
    prompt_dropdown = mo.ui.dropdown(
        options={opt["value"]: opt["label"] for opt in prompt_options},
        label="Select a Prompt",
    )
    
    model_dropdown = mo.ui.dropdown(
        options=models,
        label="Select an LLM Model",
        value="gemini-cli" if "gemini-cli" in models else list(models.keys())[0]
    )
    
    form = (
        mo.md(
            r"""
            # Prompt Library with CLI Models
            
            This notebook uses Gemini CLI directly from your terminal.
            
            {prompt_dropdown}
            {model_dropdown}
            """
        )
        .batch(
            prompt_dropdown=prompt_dropdown,
            model_dropdown=model_dropdown,
        )
        .form()
    )
    form
    return (
        categorized_prompts,
        form,
        model_dropdown,
        prompt_dropdown,
        prompt_options,
        sorted_prompt_keys,
    )


@app.cell
def __(all_prompts, form, mo, prompt_styles, re):
    selected_prompt = None
    placeholders = []
    
    if form.value and form.value["prompt_dropdown"]:
        selected_prompt = all_prompts[form.value["prompt_dropdown"]]
        
        # Extract placeholders from the prompt
        placeholders = re.findall(r'\{\{(\w+)\}\}', selected_prompt)
        
        mo.vstack([
            mo.md("### Selected Prompt:"),
            mo.md(f"```\n{selected_prompt}\n```").style(prompt_styles),
            mo.md(f"**Placeholders found:** {', '.join(placeholders) if placeholders else 'None'}")
        ])
    else:
        mo.md("*Select a prompt from the dropdown above*")
    return placeholders, selected_prompt


@app.cell
def __(mo, placeholders):
    # Create input fields for placeholders
    placeholder_inputs = {}
    
    if placeholders:
        inputs_ui = []
        for placeholder in placeholders:
            input_field = mo.ui.text(
                label=f"{placeholder}:",
                placeholder=f"Enter value for {placeholder}"
            )
            placeholder_inputs[placeholder] = input_field
            inputs_ui.append(input_field)
        
        placeholder_form = (
            mo.vstack([
                mo.md("### Fill in placeholder values:"),
                *inputs_ui,
                mo.ui.button(label="Execute Prompt", kind="success")
            ])
            .form()
        )
        placeholder_form
    else:
        placeholder_form = None
        if selected_prompt:
            # No placeholders, show execute button directly
            placeholder_form = mo.ui.button(label="Execute Prompt", kind="success").form()
            placeholder_form
    return input_field, inputs_ui, placeholder_form, placeholder_inputs


@app.cell
def __(
    cli_llm_module,
    form,
    llm_module,
    mo,
    models,
    placeholder_form,
    placeholder_inputs,
    prompt_styles,
    selected_prompt,
):
    if placeholder_form and placeholder_form.value and selected_prompt and form.value:
        # Get the filled prompt
        filled_prompt = selected_prompt
        
        # Replace placeholders with values
        if placeholder_inputs:
            for placeholder, input_field in placeholder_inputs.items():
                if hasattr(placeholder_form.value, placeholder):
                    value = getattr(placeholder_form.value, placeholder)
                    filled_prompt = filled_prompt.replace(f"{{{{{placeholder}}}}}", value)
        
        # Get selected model
        selected_model = models[form.value["model_dropdown"]]
        
        mo.md(f"**Executing with {form.value['model_dropdown']}...**")
        
        # Execute the prompt based on model type
        if "cli" in form.value["model_dropdown"]:
            # CLI model
            response = cli_llm_module.prompt_with_cli(selected_model, filled_prompt)
        else:
            # API model
            response = llm_module.prompt(selected_model, filled_prompt)
        
        # Display results
        mo.vstack([
            mo.md("### Filled Prompt:"),
            mo.md(f"```\n{filled_prompt}\n```").style(prompt_styles),
            mo.md("### Response:"),
            mo.md(f"```\n{response}\n```").style(prompt_styles),
        ])
    return filled_prompt, response, selected_model


@app.cell
def __(mo):
    mo.md(
        """
        ## Notes:
        - **Gemini CLI models** use your local Gemini CLI installation
        - **API models** (if shown) use the Gemini API key from your environment
        - Prompts are loaded from both `prompt_library/` and `testable_prompts/` directories
        - Use `{{placeholder}}` syntax in prompts for dynamic values
        """
    )
    return


if __name__ == "__main__":
    app.run()