"""Launcher for running the GUI without a console window.

When executed with ``pythonw`` (e.g. by double‑clicking the file on Windows),
any import error previously caused the program to exit silently.  This wrapper
now surfaces such errors to the user via a message box so that they know what
went wrong.
"""
from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Add the src directory to the Python path so we can import gui.
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))


def main() -> None:
    """Import the GUI module and start the Tkinter event loop."""
    try:
        import gui
    except Exception as exc:  # pragma: no cover - user facing error path
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start GUI:\n{exc}")
        root.destroy()
        return

    gui.root.mainloop()


if __name__ == "__main__":
    main()
