"""Configuration utilities for the video transcription summary GUI."""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
DEFAULT_OUTPUT_DIR = (Path(__file__).resolve().parent.parent / "summaries").resolve()


def load_config() -> dict:
    """Load configuration from CONFIG_PATH.

    Returns an empty dict if the file does not exist or is invalid.
    """
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_config(config: dict) -> None:
    """Persist configuration to CONFIG_PATH."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_default_output_dir() -> str:
    """Retrieve the default output directory from config or fallback."""
    config = load_config()
    return config.get("default_output_dir", str(DEFAULT_OUTPUT_DIR))


def set_default_output_dir(path: str) -> None:
    """Persist a new default output directory to the config file."""
    config = load_config()
    config["default_output_dir"] = path
    save_config(config)

