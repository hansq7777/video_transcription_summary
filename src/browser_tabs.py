"""Utilities for retrieving and filtering Chrome tab URLs."""
from __future__ import annotations

import requests
from yt_dlp.extractor import gen_extractors

__all__ = [
    "get_chrome_tabs",
    "filter_supported_urls",
    "get_supported_chrome_tabs",
]


def get_chrome_tabs(port: int = 9222) -> list[str]:
    """Return URLs from the Chrome instance listening on ``port``.

    The function queries Chrome's remote debugging endpoint and extracts the
    ``url`` field from each tab description.
    """
    try:
        response = requests.get(f"http://127.0.0.1:{port}/json", timeout=3)
        response.raise_for_status()
    except requests.RequestException:
        return []

    try:
        tabs = response.json()
    except ValueError:
        return []

    return [tab.get("url", "") for tab in tabs if tab.get("url")]


def filter_supported_urls(urls: list[str]) -> list[str]:
    """Filter ``urls`` keeping only those supported by ``yt_dlp`` extractors."""
    extractors = gen_extractors()
    supported = []
    for url in urls:
        for extractor in extractors:
            if extractor.suitable(url) and extractor.IE_NAME != "generic":
                supported.append(url)
                break
    return supported


def get_supported_chrome_tabs(port: int = 9222) -> list[str]:
    """Return URLs of open Chrome tabs supported by ``yt_dlp``."""
    return filter_supported_urls(get_chrome_tabs(port))
