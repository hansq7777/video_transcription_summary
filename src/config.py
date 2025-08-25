"""Configuration utilities for the video transcription summary GUI."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, set_key

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
DEFAULT_OUTPUT_DIR = (Path(__file__).resolve().parent.parent / "summaries").resolve()
DEFAULT_VIDEO_DIR = (Path(__file__).resolve().parent.parent / "videos").resolve()

# Load existing environment variables from .env if present
load_dotenv(dotenv_path=ENV_PATH)


def get_default_output_dir() -> str:
    """Retrieve the default output directory from environment or fallback."""
    return os.getenv("DEFAULT_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))


def get_default_video_dir() -> str:
    """Return the default directory for downloaded videos."""
    return os.getenv("DEFAULT_VIDEO_DIR", str(DEFAULT_VIDEO_DIR))


def set_default_output_dir(path: str) -> None:
    """Persist a new default output directory to the .env file."""
    os.environ["DEFAULT_OUTPUT_DIR"] = path
    ENV_PATH.touch(exist_ok=True)
    set_key(str(ENV_PATH), "DEFAULT_OUTPUT_DIR", path)


def get_openai_api_key() -> str | None:
    """Return the OpenAI API key from environment or .env."""
    return os.getenv("OPENAI_API_KEY")
