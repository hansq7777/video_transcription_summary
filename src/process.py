"""Utilities for downloading, transcribing and summarising audio."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

import yt_dlp
import whisper
import openai
from openai import OpenAIError

from config import get_openai_api_key

# Initialise OpenAI client using the new 1.x API style
client = openai.OpenAI(api_key=get_openai_api_key())

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


def _split_audio(audio_path: str, segment_seconds: int = 180) -> tuple[Path, list[Path]]:
    """Split ``audio_path`` into ``segment_seconds`` chunks.

    Returns a tuple of the temporary directory path and a list of segment files.
    The caller is responsible for cleaning up the temporary directory.
    """

    tmp_dir = Path(tempfile.mkdtemp(prefix="segments_"))
    ext = Path(audio_path).suffix or ".mp3"
    segment_template = tmp_dir / f"segment_%03d{ext}"
    cmd = [
        "ffmpeg",
        "-i",
        audio_path,
        "-f",
        "segment",
        "-segment_time",
        str(segment_seconds),
        "-c",
        "copy",
        str(segment_template),
    ]
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed to split audio: {e.stderr}") from e
    segments = sorted(tmp_dir.glob(f"segment_*{ext}"))
    return tmp_dir, segments


def transcribe_media(
    source: str,
    input_type: str,
    language: str,
    output_dir: str,
    model: str,
    progress_callback=None,
) -> str:
    """Download (if needed) and transcribe ``source``.

    Returns the path to the produced transcript file.
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if input_type == "audio":
        original_audio = source
        start_progress = 0
        if progress_callback:
            progress_callback(0, "Transcribing...")
    elif input_type == "url":
        start_progress = 50
        if progress_callback:
            progress_callback(0, "Downloading audio...")

        def hook(d):
            if progress_callback and d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    progress = downloaded / total * start_progress
                    progress_callback(progress, "Downloading audio...")
            elif progress_callback and d["status"] == "finished":
                progress_callback(start_progress, "Transcribing...")

        original_audio = _download_audio_from_url(source, output_dir, hook)
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    segments_dir, segments = _split_audio(original_audio)
    whisper_model = whisper.load_model(model)
    lang_code = LANGUAGE_CODES.get(language.lower(), None)
    transcripts: list[str] = []
    total_segments = len(segments) or 1
    try:
        for idx, segment in enumerate(segments, start=1):
            result = whisper_model.transcribe(str(segment), language=lang_code)
            transcripts.append(result.get("text", "").strip())
            if progress_callback:
                progress = start_progress + (idx / total_segments) * (100 - start_progress)
                progress_callback(progress, f"Transcribed {idx}/{total_segments} segments")
    finally:
        shutil.rmtree(segments_dir)

    transcript_text = "\n".join(transcripts).strip()
    transcript_path = Path(output_dir) / f"{Path(original_audio).stem}.txt"
    with transcript_path.open("w", encoding="utf-8") as f:
        f.write(transcript_text + "\n")

    if progress_callback:
        progress_callback(100, "Transcription completed")

    return str(transcript_path)


def summarize_transcript(
    transcript_path: str,
    gpt_model: str,
    prompt: str,
    progress_callback=None,
) -> str:
    """Generate a ChatGPT summary for ``transcript_path``."""

    transcript_text = Path(transcript_path).read_text(encoding="utf-8")
    if progress_callback:
        progress_callback(0, "Summarizing with ChatGPT...")
    try:
        completion = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript_text},
            ],
        )
        summary_text = completion.choices[0].message.content.strip()
        summary_path = Path(transcript_path).with_name(
            f"{Path(transcript_path).stem}_summary.txt"
        )
        with summary_path.open("w", encoding="utf-8") as f:
            f.write(summary_text + "\n")
        if progress_callback:
            progress_callback(100, "Summary completed")
        return str(summary_path)
    except OpenAIError as exc:
        if progress_callback:
            progress_callback(100, f"OpenAI API error: {exc}")
        raise


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
    """Backward compatible helper that runs transcription then summary."""

    transcript_path = transcribe_media(
        source,
        input_type,
        language,
        output_dir,
        model,
        progress_callback=progress_callback,
    )
    if prompt:
        return summarize_transcript(
            transcript_path, gpt_model, prompt, progress_callback=progress_callback
        )
    return transcript_path

