"""Main processing stub for handling video URLs or local audio files."""
from __future__ import annotations

from pathlib import Path
import tempfile

import ffmpeg
import yt_dlp


def _unify_audio_format(audio_path: str) -> str:
    """Convert an arbitrary audio file to WAV so Whisper can consume it."""
    temp_wav = Path(tempfile.mkstemp(suffix=".wav")[1])
    (
        ffmpeg.input(audio_path)
        .output(str(temp_wav), format="wav")
        .overwrite_output()
        .run(quiet=True)
    )
    return str(temp_wav)


def _download_audio_from_url(url: str, output_dir: str) -> str:
    """Download audio from a video URL and return the file path."""

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
        return str(path)


def process_media(
    source: str,
    input_type: str,
    language: str,
    output_dir: str,
    model: str,
    prompt: str,
) -> None:
    """Placeholder function representing the core processing pipeline.

    In a full implementation this would download the video, extract audio,
    generate transcripts and summaries, etc. For now it simply prints the
    received parameters so the GUI wiring can be verified. If the input is a
    local audio file it is converted to WAV first so it is compatible with
    Whisper.
    """

    print("Processing media with parameters:")
    print(f"Source: {source}")
    print(f"Input Type: {input_type}")
    print(f"Language: {language}")
    print(f"Output Directory: {output_dir}")
    print(f"ChatGPT Model: {model}")
    print(f"Prompt: {prompt}")

    if input_type == "audio":
        unified = _unify_audio_format(source)
        print(f"Unified audio file: {unified}")
    elif input_type == "url":
        try:
            downloaded = _download_audio_from_url(source, output_dir)
            print(f"Downloaded audio file: {downloaded}")
            unified = _unify_audio_format(downloaded)
            print(f"Unified audio file: {unified}")
        except Exception as exc:
            print(f"Error downloading audio: {exc}")

