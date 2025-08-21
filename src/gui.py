"""Tkinter-based GUI for configuring and running video transcription summaries."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from config import get_default_output_dir, set_default_output_dir
from process import process_media


def browse_output_dir() -> None:
    """Open a directory chooser and update the output directory selection."""
    path = filedialog.askdirectory(initialdir=output_dir_var.get())
    if path:
        output_dir_var.set(path)
        set_default_output_dir(path)


def browse_audio_file() -> None:
    """Open a file chooser and update the audio file selection."""
    path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg")]
    )
    if path:
        audio_file_var.set(path)


def toggle_input_fields() -> None:
    """Enable fields based on the selected input type."""
    if input_type_var.get() == "url":
        url_entry.config(state="normal")
        audio_entry.config(state="disabled")
        audio_browse.config(state="disabled")
    else:
        url_entry.config(state="disabled")
        audio_entry.config(state="normal")
        audio_browse.config(state="normal")


def run() -> None:
    """Invoke the main processing function with the provided parameters."""
    source = url_var.get() if input_type_var.get() == "url" else audio_file_var.get()
    status_var.set("Transcribing...")
    root.update_idletasks()
    try:
        transcript = process_media(
            source,
            input_type_var.get(),
            language_var.get(),
            output_dir_var.get(),
            model_var.get(),
            prompt_var.get(),
        )
        status_var.set(f"Completed: {transcript}")
    except Exception as exc:  # pragma: no cover - GUI error path
        status_var.set("Error")
        messagebox.showerror("Error", str(exc))
    set_default_output_dir(output_dir_var.get())


root = tk.Tk()
root.title("Video Transcription Summary")

# Input type selection
input_type_var = tk.StringVar(value="url")
tk.Label(root, text="Input Type:").grid(row=0, column=0, sticky="e")
tk.Radiobutton(
    root, text="URL", variable=input_type_var, value="url", command=toggle_input_fields
).grid(row=0, column=1, sticky="w")
tk.Radiobutton(
    root,
    text="Audio File",
    variable=input_type_var,
    value="audio",
    command=toggle_input_fields,
).grid(row=0, column=2, sticky="w")

# URL field
url_var = tk.StringVar()
tk.Label(root, text="Video URL:").grid(row=1, column=0, sticky="e")
url_entry = tk.Entry(root, textvariable=url_var, width=50)
url_entry.grid(row=1, column=1, padx=5, pady=5)

# Audio file selector
audio_file_var = tk.StringVar()
tk.Label(root, text="Audio File:").grid(row=2, column=0, sticky="e")
audio_entry = tk.Entry(root, textvariable=audio_file_var, width=40)
audio_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
audio_browse = tk.Button(root, text="Browse", command=browse_audio_file)
audio_browse.grid(row=2, column=2, padx=5, pady=5)

# Language dropdown
languages = ["English", "Spanish", "French", "German"]
language_var = tk.StringVar(value=languages[0])
tk.Label(root, text="Language:").grid(row=3, column=0, sticky="e")
tk.OptionMenu(root, language_var, *languages).grid(
    row=3, column=1, padx=5, pady=5, sticky="w"
)

# Output folder selector
output_dir_var = tk.StringVar(value=get_default_output_dir())
tk.Label(root, text="Output Folder:").grid(row=4, column=0, sticky="e")
tk.Entry(root, textvariable=output_dir_var, width=40).grid(
    row=4, column=1, padx=5, pady=5, sticky="w"
)
tk.Button(root, text="Browse", command=browse_output_dir).grid(
    row=4, column=2, padx=5, pady=5
)

# ChatGPT model
model_var = tk.StringVar(value="gpt-3.5-turbo")
tk.Label(root, text="ChatGPT Model:").grid(row=5, column=0, sticky="e")
tk.Entry(root, textvariable=model_var, width=50).grid(row=5, column=1, padx=5, pady=5)

# Prompt
prompt_var = tk.StringVar()
tk.Label(root, text="Prompt:").grid(row=6, column=0, sticky="e")
tk.Entry(root, textvariable=prompt_var, width=50).grid(row=6, column=1, padx=5, pady=5)

# Run button
run_button = tk.Button(root, text="Run", command=run)
run_button.grid(row=7, column=1, pady=10)

# Status label
status_var = tk.StringVar(value="")
tk.Label(root, textvariable=status_var).grid(row=8, column=1, pady=5)

toggle_input_fields()


if __name__ == "__main__":
    root.mainloop()

