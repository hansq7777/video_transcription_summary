"""Launcher for running the GUI without a console window."""
from __future__ import annotations

import sys
from pathlib import Path

# Add the src directory to the Python path so we can import gui
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

import gui  # noqa: E402

if __name__ == "__main__":
    gui.root.mainloop()
