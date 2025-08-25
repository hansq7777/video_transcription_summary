"""Configuration utilities for the video transcription summary GUI."""
from __future__ import annotations

import os
from pathlib import Path

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv, set_key
except Exception:  # pragma: no cover - provide minimal fallbacks
    def load_dotenv(*args, **kwargs):
        path = kwargs.get("dotenv_path") or (args[0] if args else None)
        if not path:
            return False
        path = Path(path)
        if not path.exists():
            return False
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())
        return True

    def set_key(file_path: str, key: str, value: str) -> None:
        file = Path(file_path)
        if file.exists():
            lines = file.read_text(encoding="utf-8").splitlines()
        else:
            lines = []
        updated = False
        for i, line in enumerate(lines):
            if line.split("=", 1)[0] == key:
                lines[i] = f"{key}={value}"
                updated = True
                break
        if not updated:
            lines.append(f"{key}={value}")
        file.write_text("\n".join(lines) + "\n", encoding="utf-8")

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
