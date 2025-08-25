"""Utilities for retrieving and filtering Chrome tab URLs."""
from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import urlopen
from urllib.parse import urlparse
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
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as response:
            tabs = json.load(response)
    except (URLError, json.JSONDecodeError):
        return []

    return [tab.get("url", "") for tab in tabs if tab.get("url")]


def filter_supported_urls(urls: list[str]) -> list[str]:
    """Filter ``urls`` keeping only those supported by ``yt_dlp`` extractors."""
    extractors = gen_extractors()
    supported = []
    for url in urls:
        # Skip service worker scripts which are not downloadable media.
        if urlparse(url).path.lower().endswith("service-worker.js"):
            continue
        for extractor in extractors:
            if extractor.suitable(url) and extractor.IE_NAME != "generic":
                supported.append(url)
                break
    return supported


def get_supported_chrome_tabs(port: int = 9222) -> list[str]:
    """Return URLs of open Chrome tabs supported by ``yt_dlp``."""
    return filter_supported_urls(get_chrome_tabs(port))
