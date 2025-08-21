"""Tkinter-based GUI for configuring and running video transcription summaries."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog

from config import get_default_output_dir, set_default_output_dir
from process import process_video


def browse_output_dir() -> None:
    """Open a directory chooser and update the output directory selection."""
    path = filedialog.askdirectory(initialdir=output_dir_var.get())
    if path:
        output_dir_var.set(path)
        set_default_output_dir(path)


def run() -> None:
    """Invoke the main processing function with the provided parameters."""
    process_video(
        url_var.get(),
        language_var.get(),
        output_dir_var.get(),
        model_var.get(),
        prompt_var.get(),
    )
    set_default_output_dir(output_dir_var.get())


root = tk.Tk()
root.title("Video Transcription Summary")

# URL field
url_var = tk.StringVar()
tk.Label(root, text="Video URL:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=url_var, width=50).grid(row=0, column=1, padx=5, pady=5)

# Language dropdown
languages = ["English", "Spanish", "French", "German"]
language_var = tk.StringVar(value=languages[0])
tk.Label(root, text="Language:").grid(row=1, column=0, sticky="e")
tk.OptionMenu(root, language_var, *languages).grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Output folder selector
output_dir_var = tk.StringVar(value=get_default_output_dir())
tk.Label(root, text="Output Folder:").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=output_dir_var, width=40).grid(row=2, column=1, padx=5, pady=5, sticky="w")
tk.Button(root, text="Browse", command=browse_output_dir).grid(row=2, column=2, padx=5, pady=5)

# ChatGPT model
model_var = tk.StringVar(value="gpt-3.5-turbo")
tk.Label(root, text="ChatGPT Model:").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=model_var, width=50).grid(row=3, column=1, padx=5, pady=5)

# Prompt
prompt_var = tk.StringVar()
tk.Label(root, text="Prompt:").grid(row=4, column=0, sticky="e")
tk.Entry(root, textvariable=prompt_var, width=50).grid(row=4, column=1, padx=5, pady=5)

# Run button
run_button = tk.Button(root, text="Run", command=run)
run_button.grid(row=5, column=1, pady=10)


if __name__ == "__main__":
    root.mainloop()

