import tkinter as tk
from tkinter import scrolledtext
import random

def extract_placeholders():
    """
    Scans the base prompt for occurrences of the token "x" (used as a placeholder)
    and creates an input field for each found placeholder.
    """
    base = base_prompt_text.get("1.0", tk.END)
    # Tokenize by whitespace and count only tokens that exactly match "x"
    tokens = base.split()
    placeholders_count = tokens.count("x")
    
    # Clear any previously created fields
    for widget in placeholder_frame.winfo_children():
        widget.destroy()
    placeholder_entries.clear()
    
    # Create an entry field for each placeholder found
    for i in range(placeholders_count):
        label = tk.Label(placeholder_frame, text=f"Placeholder {i+1} (for 'x'):")
        label.grid(row=i, column=0, padx=5, pady=2, sticky='w')
        entry = tk.Entry(placeholder_frame, width=40)
        entry.grid(row=i, column=1, padx=5, pady=2)
        placeholder_entries.append(entry)

def generate_prompts():
    """
    Generates a number of outputs by replacing each occurrence of "x" in the base prompt
    with the corresponding placeholder entry. If a placeholder entry has multiple comma‐separated
    options, one is chosen at random.
    """
    base = base_prompt_text.get("1.0", tk.END)
    
    try:
        num_outputs = int(num_outputs_entry.get())
    except ValueError:
        num_outputs = 1
    
    # Gather replacement options for each placeholder field
    placeholder_values = []
    for entry in placeholder_entries:
        text = entry.get().strip()
        if text:
            # Allow multiple options by splitting on commas
            options = [opt.strip() for opt in text.split(",") if opt.strip()]
        else:
            options = [""]
        placeholder_values.append(options)
    
    outputs = []
    for _ in range(num_outputs):
        # Start with the original base prompt
        result = base
        # Replace each placeholder occurrence (only the first occurrence each time)
        for opts in placeholder_values:
            chosen = random.choice(opts)
            result = result.replace("x", chosen, 1)
        outputs.append(result)
    
    # Display generated outputs
    output_text.delete("1.0", tk.END)
    for i, out in enumerate(outputs):
        output_text.insert(tk.END, f"Prompt {i+1}:\n{out}\n{'-'*40}\n")
