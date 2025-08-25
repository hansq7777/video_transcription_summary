"""Tkinter GUI for transcribing audio and generating summaries."""
from __future__ import annotations

import importlib
import threading
import tkinter as tk
from pathlib import Path
from types import ModuleType
from tkinter import filedialog, messagebox, ttk

from config import get_default_output_dir, get_default_video_dir, set_default_output_dir

# ``process`` and its heavy dependencies are imported lazily in the background so
# the GUI can appear quickly.
process: ModuleType | None = None


def load_process_module() -> None:
    """Import the heavy ``process`` module in a background thread."""

    global process
    try:
        process = importlib.import_module("process")
    except Exception as exc:  # pragma: no cover - import error path
        print(f"Failed to load dependencies: {exc}")


def ensure_process_loaded() -> ModuleType:
    """Ensure the ``process`` module is available and return it."""

    global process
    if process is None:
        load_process_module()
    assert process is not None  # for type checkers
    return process


audio_files: list[str] = []


def browse_output_dir() -> None:
    """Open a directory chooser and update the output directory selection."""
    path = filedialog.askdirectory(initialdir=output_dir_var.get())
    if path:
        output_dir_var.set(path)
        set_default_output_dir(path)


def browse_audio_file() -> None:
    """Open a file chooser and update the audio file selection."""
    paths = filedialog.askopenfilenames(
        filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg")]
    )
    if paths:
        audio_files.clear()
        audio_files.extend(paths)
        audio_file_var.set(f"{len(paths)} files selected")


def toggle_input_fields() -> None:
    """Enable fields based on the selected input type."""
    if input_type_var.get() == "url":
        url_text.config(state="normal")
        audio_entry.config(state="disabled")
        audio_browse.config(state="disabled")
    else:
        url_text.config(state="disabled")
        audio_entry.config(state="readonly")
        audio_browse.config(state="normal")


def start_download_video() -> None:
    """Download videos from the provided URLs."""
    if input_type_var.get() != "url":
        messagebox.showwarning("Invalid input", "Please enter video URLs to download")
        return

    sources = [
        line.strip()
        for line in url_text.get("1.0", tk.END).splitlines()
        if line.strip()
    ]
    if not sources:
        messagebox.showwarning("Missing source", "Please provide a URL.")
        return

    transcribe_progress_var.set(0)
    transcribe_status_var.set("Starting...")

    def update_progress(percent: float, status: str | None = None) -> None:
        def _update() -> None:
            transcribe_progress_var.set(percent)
            if status is not None:
                transcribe_status_var.set(status)

        root.after(0, _update)

    def task() -> None:
        try:
            module = ensure_process_loaded()
            paths = module.download_videos(
                sources,
                get_default_video_dir(),
                progress_callback=update_progress,
            )
            root.after(0, lambda: transcribe_status_var.set(f"Saved videos: {', '.join(paths)}"))
        except Exception as exc:  # pragma: no cover - GUI error path
            error_message = str(exc)
            root.after(0, lambda: transcribe_status_var.set("Error"))
            root.after(0, lambda msg=error_message: messagebox.showerror("Error", msg))

    threading.Thread(target=task, daemon=True).start()


def start_audio_conversion() -> None:
    """Download videos and convert them to audio files."""
    if input_type_var.get() != "url":
        messagebox.showwarning("Invalid input", "Please enter video URLs to convert")
        return

    sources = [
        line.strip()
        for line in url_text.get("1.0", tk.END).splitlines()
        if line.strip()
    ]
    if not sources:
        messagebox.showwarning("Missing source", "Please provide a URL.")
        return

    transcribe_progress_var.set(0)
    transcribe_status_var.set("Starting...")

    def update_progress(percent: float, status: str | None = None) -> None:
        def _update() -> None:
            transcribe_progress_var.set(percent)
            if status is not None:
                transcribe_status_var.set(status)

        root.after(0, _update)

    def task() -> None:
        try:
            module = ensure_process_loaded()
            paths = module.convert_to_audio_batch(
                sources,
                output_dir_var.get(),
                progress_callback=update_progress,
            )
            audio_files.clear()
            audio_files.extend(paths)
            root.after(0, lambda: audio_file_var.set(f"{len(paths)} files saved"))
            root.after(0, lambda: transcribe_status_var.set(f"Saved audio: {', '.join(paths)}"))
        except Exception as exc:  # pragma: no cover - GUI error path
            error_message = str(exc)
            root.after(0, lambda: transcribe_status_var.set("Error"))
            root.after(0, lambda msg=error_message: messagebox.showerror("Error", msg))

    threading.Thread(target=task, daemon=True).start()


def start_transcription() -> None:
    """Run the transcription step in a background thread."""
    if input_type_var.get() == "url":
        sources = [
            line.strip()
            for line in url_text.get("1.0", tk.END).splitlines()
            if line.strip()
        ]
    else:
        sources = audio_files.copy()

    if not sources:
        messagebox.showwarning(
            "Missing source", "Please provide a URL or audio file."
        )
        return

    transcribe_progress_var.set(0)
    transcribe_status_var.set("Starting...")

    def update_progress(percent: float, status: str | None = None) -> None:
        def _update() -> None:
            transcribe_progress_var.set(percent)
            if status is not None:
                transcribe_status_var.set(status)

        root.after(0, _update)

    def task() -> None:
        try:
            module = ensure_process_loaded()
            paths = module.transcribe_batch(
                sources,
                input_type_var.get(),
                language_var.get(),
                whisper_model_var.get(),
                output_dir_var.get(),
                progress_callback=update_progress,
            )
            transcript_path_var.set(paths[0] if paths else "")
            texts = []
            for p in paths:
                t = Path(p).read_text(encoding="utf-8")
                texts.append(f"--- {Path(p).name} ---\n{t}")
            combined = "\n\n".join(texts)
            root.after(0, lambda: transcript_text.delete("1.0", tk.END))
            root.after(0, lambda: transcript_text.insert(tk.END, combined))
            root.after(0, lambda: transcribe_status_var.set(f"Saved transcripts: {', '.join(paths)}"))
        except Exception as exc:  # pragma: no cover - GUI error path
            error_message = str(exc)
            root.after(0, lambda: transcribe_status_var.set("Error"))
            root.after(0, lambda msg=error_message: messagebox.showerror("Error", msg))
        finally:
            set_default_output_dir(output_dir_var.get())

    threading.Thread(target=task, daemon=True).start()


def start_summary() -> None:
    """Run the ChatGPT summarisation in a background thread."""
    path = transcript_path_var.get()
    if not path:
        messagebox.showwarning("No transcript", "Run transcription first.")
        return

    Path(path).write_text(transcript_text.get("1.0", tk.END).strip(), encoding="utf-8")
    summary_progress_var.set(0)
    summary_status_var.set("Starting...")

    def update_progress(percent: float, status: str | None = None) -> None:
        def _update() -> None:
            summary_progress_var.set(percent)
            if status is not None:
                summary_status_var.set(status)

        root.after(0, _update)

    def task() -> None:
        try:
            module = ensure_process_loaded()
            summary_path = module.summarize_transcript(
                path,
                gpt_model_var.get(),
                prompt_var.get(),
                progress_callback=update_progress,
            )
            text = Path(summary_path).read_text(encoding="utf-8")
            root.after(0, lambda: summary_output.delete("1.0", tk.END))
            root.after(0, lambda: summary_output.insert(tk.END, text))
            root.after(0, lambda: summary_status_var.set(f"Saved summary: {summary_path}"))
        except Exception as exc:  # pragma: no cover - GUI error path
            error_message = str(exc)
            root.after(0, lambda: summary_status_var.set("Error"))
            root.after(0, lambda msg=error_message: messagebox.showerror("Error", msg))

    threading.Thread(target=task, daemon=True).start()


root = tk.Tk()
root.title("Video Transcription Summary")

# ---------------- Transcription section ----------------
transcribe_frame = tk.LabelFrame(root, text="Audio Transcription")
transcribe_frame.pack(fill="x", padx=10, pady=5)

input_type_var = tk.StringVar(value="url")
tk.Label(transcribe_frame, text="Input Type:").grid(row=0, column=0, sticky="e")
tk.Radiobutton(
    transcribe_frame,
    text="URL",
    variable=input_type_var,
    value="url",
    command=toggle_input_fields,
).grid(row=0, column=1, sticky="w")
tk.Radiobutton(
    transcribe_frame,
    text="Audio File",
    variable=input_type_var,
    value="audio",
    command=toggle_input_fields,
).grid(row=0, column=2, sticky="w")

tk.Label(transcribe_frame, text="Video URLs:").grid(row=1, column=0, sticky="ne")
url_text = tk.Text(transcribe_frame, height=4, width=50)
url_text.grid(row=1, column=1, padx=5, pady=2, columnspan=2, sticky="w")

audio_file_var = tk.StringVar()
tk.Label(transcribe_frame, text="Audio Files:").grid(row=2, column=0, sticky="e")
audio_entry = tk.Entry(transcribe_frame, textvariable=audio_file_var, width=40, state="readonly")
audio_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
audio_browse = tk.Button(transcribe_frame, text="Browse", command=browse_audio_file)
audio_browse.grid(row=2, column=2, padx=5, pady=2)

languages = ["English", "中文", "日本語", "Deutsch"]
language_var = tk.StringVar(value=languages[0])
tk.Label(transcribe_frame, text="Language:").grid(row=3, column=0, sticky="e")
tk.OptionMenu(transcribe_frame, language_var, *languages).grid(
    row=3, column=1, padx=5, pady=2, sticky="w"
)

output_dir_var = tk.StringVar(value=get_default_output_dir())
tk.Label(transcribe_frame, text="Output Folder:").grid(row=4, column=0, sticky="e")
tk.Entry(transcribe_frame, textvariable=output_dir_var, width=40).grid(
    row=4, column=1, padx=5, pady=2, sticky="w"
)
tk.Button(transcribe_frame, text="Browse", command=browse_output_dir).grid(
    row=4, column=2, padx=5, pady=2
)

whisper_models = ["tiny", "base", "small", "medium", "large"]
whisper_model_var = tk.StringVar(value="small")
tk.Label(transcribe_frame, text="Whisper Model:").grid(row=5, column=0, sticky="e")
tk.OptionMenu(transcribe_frame, whisper_model_var, *whisper_models).grid(
    row=5, column=1, padx=5, pady=2, sticky="w"
)

download_button = tk.Button(
    transcribe_frame, text="Download Video", command=start_download_video
)
download_button.grid(row=6, column=0, pady=5)

audio_button = tk.Button(
    transcribe_frame, text="To Audio", command=start_audio_conversion
)
audio_button.grid(row=6, column=1, pady=5)

transcribe_button = tk.Button(
    transcribe_frame, text="Transcribe", command=start_transcription
)
transcribe_button.grid(row=6, column=2, pady=5)

transcribe_progress_var = tk.DoubleVar(value=0)
ttk.Progressbar(transcribe_frame, variable=transcribe_progress_var, maximum=100).grid(
    row=7, column=0, columnspan=3, padx=5, pady=2, sticky="we"
)

transcribe_status_var = tk.StringVar(value="")
tk.Label(transcribe_frame, textvariable=transcribe_status_var).grid(
    row=8, column=0, columnspan=3
)

# ---------------- Summary section ----------------
summary_frame = tk.LabelFrame(root, text="ChatGPT Summary")
summary_frame.pack(fill="both", expand=True, padx=10, pady=5)

gpt_model_var = tk.StringVar(value="gpt-3.5-turbo")
tk.Label(summary_frame, text="ChatGPT Model:").grid(row=0, column=0, sticky="e")
tk.Entry(summary_frame, textvariable=gpt_model_var, width=40).grid(
    row=0, column=1, padx=5, pady=2, sticky="w"
)

prompt_var = tk.StringVar()
tk.Label(summary_frame, text="Prompt:").grid(row=1, column=0, sticky="e")
tk.Entry(summary_frame, textvariable=prompt_var, width=40).grid(
    row=1, column=1, padx=5, pady=2, sticky="w"
)

tk.Label(summary_frame, text="Transcript:").grid(row=2, column=0, sticky="ne")
transcript_text = tk.Text(summary_frame, height=8, width=60)
transcript_text.grid(row=2, column=1, padx=5, pady=2)

tk.Label(summary_frame, text="Summary:").grid(row=3, column=0, sticky="ne")
summary_output = tk.Text(summary_frame, height=8, width=60)
summary_output.grid(row=3, column=1, padx=5, pady=2)

summarize_button = tk.Button(summary_frame, text="Summarize", command=start_summary)
summarize_button.grid(row=4, column=1, pady=5)

summary_progress_var = tk.DoubleVar(value=0)
ttk.Progressbar(summary_frame, variable=summary_progress_var, maximum=100).grid(
    row=5, column=0, columnspan=2, padx=5, pady=2, sticky="we"
)

summary_status_var = tk.StringVar(value="")
tk.Label(summary_frame, textvariable=summary_status_var).grid(
    row=6, column=0, columnspan=2
)

transcript_path_var = tk.StringVar(value="")

toggle_input_fields()

# Begin loading heavy dependencies after the UI is ready.
threading.Thread(target=load_process_module, daemon=True).start()

if __name__ == "__main__":
    root.mainloop()

