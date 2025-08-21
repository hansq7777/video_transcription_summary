"""Utilities for downloading and transcribing audio."""
from __future__ import annotations

from pathlib import Path

import yt_dlp
import whisper
import openai
from openai.error import OpenAIError

# Mapping of UI language names to whisper language codes
LANGUAGE_CODES = {
    "english": "en",
    "中文": "zh",
    "日本語": "ja",
    "deutsch": "de",
}


def _download_audio_from_url(
    url: str, output_dir: str, progress_hook=None
) -> str:
    """Download audio from a video URL and return the file path."""

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    if progress_hook is not None:
        ydl_opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
        return str(path)


def process_media(
    source: str,
    input_type: str,
    language: str,
    output_dir: str,
    model: str,
    gpt_model: str,
    prompt: str,
    progress_callback=None,
) -> str:
    """Transcribe the provided media source using Whisper.

    Parameters
    ----------
    source: str
        Path to a local audio file or a video URL depending on ``input_type``.
    input_type: str
        Either ``"audio"`` for local files or ``"url"`` for remote videos.
    language: str
        Human-readable language name selected in the GUI.
    output_dir: str
        Directory where the transcript text file will be stored.
    model: str
        Name of the Whisper model to use for transcription.

    Returns
    -------
    str
        Path to the generated transcript file.
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Determine audio source
    if input_type == "audio":
        original_audio = source
    elif input_type == "url":
        if progress_callback:
            progress_callback(0, "Downloading audio...")

        def hook(d):
            if progress_callback and d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    progress = downloaded / total * 33
                    progress_callback(progress, "Downloading audio...")
            elif progress_callback and d["status"] == "finished":
                progress_callback(33, "Transcribing...")

        original_audio = _download_audio_from_url(source, output_dir, hook)
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    if progress_callback and input_type == "audio":
        progress_callback(33, "Transcribing...")

    # Load the Whisper model and transcribe with the selected language
    whisper_model = whisper.load_model(model)
    lang_code = LANGUAGE_CODES.get(language.lower(), None)
    result = whisper_model.transcribe(original_audio, language=lang_code)
    if progress_callback:
        progress_callback(66, "Summarizing with ChatGPT...")
    transcript_text = result.get("text", "").strip()

    # Save transcript to the specified output directory
    transcript_path = Path(output_dir) / f"{Path(original_audio).stem}.txt"
    with transcript_path.open("w", encoding="utf-8") as f:
        f.write(transcript_text + "\n")

    # Read back the transcript from disk
    transcript_text = transcript_path.read_text(encoding="utf-8")

    summary_text = ""
    summary_path = transcript_path
    if prompt:
        try:
            completion = openai.ChatCompletion.create(
                model=gpt_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcript_text},
                ],
            )
            summary_text = completion.choices[0].message["content"].strip()
            summary_path = transcript_path.with_name(
                f"{transcript_path.stem}_summary.txt"
            )
            with summary_path.open("w", encoding="utf-8") as f:
                f.write(summary_text + "\n")
        except OpenAIError as exc:
            if progress_callback:
                progress_callback(100, f"OpenAI API error: {exc}")
            raise

    if progress_callback:
        progress_callback(100, "Completed")

    return str(summary_path)

