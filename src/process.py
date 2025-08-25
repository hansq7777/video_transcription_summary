"""Utilities for downloading, transcribing and summarising audio."""
from __future__ import annotations

from pathlib import Path
import math
import shutil
import subprocess
import tempfile

import yt_dlp
import whisper

# OpenAI is imported lazily to avoid heavy startup cost when the ChatGPT API
# is not used.  ``openai`` and ``OpenAIError`` are loaded within
# :func:`get_openai_client`.
openai = None
OpenAIError = Exception

from config import (
    get_openai_api_key,
    get_default_output_dir,
    get_default_video_dir,
)

# Lazily constructed OpenAI client.  ``None`` until ``get_openai_client`` is
# first called from ``summarize_transcript``.
client = None


def get_openai_client():
    """Return a cached OpenAI client, creating it on first use."""

    global client, openai, OpenAIError
    if client is None:
        import openai as _openai
        from openai import OpenAIError as _OpenAIError

        openai = _openai
        OpenAIError = _OpenAIError
        client = openai.OpenAI(api_key=get_openai_api_key())
    return client

# Mapping of UI language names to whisper language codes
LANGUAGE_CODES = {
    "english": "en",
    "中文": "zh",
    "日本語": "ja",
    "deutsch": "de",
}


def download_video(
    url: str,
    output_dir: str | None = None,
    progress_hook=None,
    format_spec: str = "bestvideo+bestaudio/best",
) -> str:
    """Download media from ``url`` using ``format_spec`` and return the file path.

    The default ``format_spec`` selects the highest quality video combined with the
    best available audio stream.  Supplying a different ``format_spec`` allows
    callers to prefer audio-only downloads or other combinations supported by
    ``yt-dlp``.
    """

    if output_dir is None:
        output_dir = get_default_video_dir()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": format_spec,
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


def convert_video_to_audio(video_path: str, output_dir: str) -> str:
    """Convert ``video_path`` to an MP3 file in ``output_dir``."""

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    audio_path = Path(output_dir) / f"{Path(video_path).stem}.mp3"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "libmp3lame",
        str(audio_path),
    ]
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed to convert video: {e.stderr}") from e
    return str(audio_path)


def download_to_audio(
    url: str, output_dir: str | None = None, progress_callback=None
) -> str:
    """Download ``url`` and convert to audio, returning the audio path."""

    if output_dir is None:
        output_dir = get_default_output_dir()
    if progress_callback:
        progress_callback(0, "Downloading audio...")

    def hook(d):
        if progress_callback and d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                progress = downloaded / total * 50
                progress_callback(progress, "Downloading audio...")
        elif progress_callback and d["status"] == "finished":
            progress_callback(50, "Converting to audio...")

    # Prefer downloading the best audio-only stream. If that's not available,
    # fall back to the lowest-quality video with the best audio to conserve
    # bandwidth while preserving audio fidelity.
    fmt = "bestaudio/worstvideo+bestaudio/best"
    video_path = download_video(url, output_dir, hook, format_spec=fmt)
    audio_path = convert_video_to_audio(video_path, output_dir)
    if progress_callback:
        progress_callback(100, "Audio conversion completed")
    return audio_path


def download_videos(
    urls: list[str],
    output_dir: str | None = None,
    progress_callback=None,
) -> list[str]:
    """Download multiple videos sequentially."""

    if output_dir is None:
        output_dir = get_default_video_dir()
    videos: list[str] = []
    total = len(urls) or 1
    for index, url in enumerate(urls, start=1):
        base = (index - 1) * 100 / total

        def hook(d):
            if progress_callback and d["status"] == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total_bytes:
                    progress = base + downloaded / total_bytes * (100 / total)
                    progress_callback(progress, f"Downloading {index}/{total} videos...")
            elif progress_callback and d["status"] == "finished":
                progress_callback(base + 100 / total, f"Downloaded {index}/{total} videos")

        videos.append(download_video(url, output_dir, hook))

    if progress_callback:
        progress_callback(100, "Video download completed")
    return videos


def convert_to_audio_batch(
    urls: list[str],
    output_dir: str | None = None,
    progress_callback=None,
) -> list[str]:
    """Download videos and convert them to audio sequentially."""

    if output_dir is None:
        output_dir = get_default_output_dir()
    audios: list[str] = []
    total = len(urls) or 1
    for index, url in enumerate(urls, start=1):
        base = (index - 1) * 100 / total

        def cb(p, status=None):
            if progress_callback:
                progress = base + p / total
                progress_callback(progress, status)

        audios.append(download_to_audio(url, output_dir, progress_callback=cb))

    if progress_callback:
        progress_callback(100, "Audio conversion completed")
    return audios


def _get_media_duration(path: str) -> float:
    """Return the duration of the media file in seconds using ``ffprobe``."""

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed to get duration: {e.stderr}") from e
    return float(result.stdout.strip())


def _split_audio(audio_path: str, segment_seconds: float) -> tuple[Path, list[Path]]:
    """Split ``audio_path`` into chunks of ``segment_seconds`` seconds."""

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
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed to split audio: {e.stderr}") from e
    segments = sorted(tmp_dir.glob(f"segment_*{ext}"))
    return tmp_dir, segments


def transcribe_media(
    source: str,
    input_type: str,
    language: str,
    output_dir: str | None,
    model: str,
    progress_callback=None,
) -> str:
    """Download (if needed) and transcribe ``source``.

    Returns the path to the produced transcript file.
    """

    if output_dir is None:
        output_dir = get_default_output_dir()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if input_type == "audio":
        audio_path = source
        start_progress = 0
        if progress_callback:
            progress_callback(0, "Transcribing...")
    elif input_type == "url":
        def cb(p: float, status: str | None = None) -> None:
            if progress_callback:
                progress_callback(p * 0.66, status)

        audio_path = download_to_audio(source, output_dir, progress_callback=cb)
        start_progress = 66
        if progress_callback:
            progress_callback(start_progress, "Transcribing...")
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    duration = _get_media_duration(audio_path)
    if duration <= 900:
        segments_dir = None
        segments = [Path(audio_path)]
    else:
        segment_count = math.ceil(duration / 900)
        segment_time = duration / segment_count
        segments_dir, segments = _split_audio(audio_path, segment_time)

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
        if segments_dir is not None:
            shutil.rmtree(segments_dir)

    transcript_text = "\n".join(transcripts).strip()
    transcript_path = Path(output_dir) / f"{Path(audio_path).stem}.txt"
    with transcript_path.open("w", encoding="utf-8") as f:
        f.write(transcript_text + "\n")

    if progress_callback:
        progress_callback(100, "Transcription completed")

    return str(transcript_path)


def transcribe_batch(
    sources: list[str],
    input_type: str,
    language: str,
    model: str,
    output_dir: str | None = None,
    progress_callback=None,
) -> list[str]:
    """Transcribe multiple ``sources`` sequentially.

    Each source is processed in order and the resulting transcript paths are
    returned as a list. Progress is reported as an overall percentage across the
    entire batch.
    """

    if output_dir is None:
        output_dir = get_default_output_dir()
    transcripts: list[str] = []
    total = len(sources) or 1
    for index, src in enumerate(sources, start=1):
        base = (index - 1) * 100 / total

        def cb(p: float, status: str | None = None) -> None:
            if progress_callback:
                overall = base + p / total
                progress_callback(overall, status)

        path = transcribe_media(
            src,
            input_type,
            language,
            output_dir,
            model,
            progress_callback=cb,
        )
        transcripts.append(path)

    if progress_callback:
        progress_callback(100, "Transcription completed")

    return transcripts


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
    client = get_openai_client()
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
    output_dir: str | None,
    model: str,
    gpt_model: str,
    prompt: str,
    progress_callback=None,
) -> str:
    """Backward compatible helper that runs transcription then summary."""
    if output_dir is None:
        output_dir = get_default_output_dir()
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

