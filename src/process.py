"""Utilities for downloading, normalizing and transcribing audio."""
from __future__ import annotations

from pathlib import Path
import tempfile

import ffmpeg
import yt_dlp
import whisper

# Mapping of UI language names to whisper language codes
LANGUAGE_CODES = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
}


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
        original_audio = _download_audio_from_url(source, output_dir)
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    unified = _unify_audio_format(original_audio)

    # Load the Whisper model and transcribe with the selected language
    whisper_model = whisper.load_model("base")
    lang_code = LANGUAGE_CODES.get(language.lower(), None)
    result = whisper_model.transcribe(unified, language=lang_code)
    transcript_text = result.get("text", "").strip()

    # Save transcript to the specified output directory
    transcript_path = Path(output_dir) / f"{Path(original_audio).stem}.txt"
    with transcript_path.open("w", encoding="utf-8") as f:
        f.write(transcript_text + "\n")

    # Cleanup temporary WAV file
    Path(unified).unlink(missing_ok=True)

    return str(transcript_path)

