"""Main processing stub for video transcription summary."""
from __future__ import annotations


def process_video(url: str, language: str, output_dir: str, model: str, prompt: str) -> None:
    """Placeholder function representing the core processing pipeline.

    In a full implementation this would download the video, extract audio,
    generate transcripts and summaries, etc. For now it simply prints the
    received parameters so the GUI wiring can be verified.
    """
    print("Processing video with parameters:")
    print(f"URL: {url}")
    print(f"Language: {language}")
    print(f"Output Directory: {output_dir}")
    print(f"ChatGPT Model: {model}")
    print(f"Prompt: {prompt}")

