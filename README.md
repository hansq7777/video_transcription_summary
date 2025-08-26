# Video Transcription Summary

This project downloads videos, extracts audio, generates transcripts and summarises the content. Transcription relies on local OpenAI Whisper models, so the ``openai-whisper`` package must be installed. The GUI allows entering one or more video URLs or selecting multiple local audio files. Each source is transcribed in sequence and written to its own transcript file. By default, audio downloads and transcripts are stored under a `summaries` folder while full video downloads go to a `videos` folder; these directories are created automatically when needed.

All downloads and transcription actions are logged to a `work.log` file in the project root so you can review past activity.

## Installation

1. Install [ffmpeg](https://ffmpeg.org/) on your system.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   The optional [yt-dlp](https://github.com/yt-dlp/yt-dlp) dependency enables the
   *Load Tabs* feature to detect supported video sites. If it is missing the
   application will simply return no tabs. The ``openai-whisper`` dependency is
   required for transcription and is included in ``requirements.txt``.
3. (Optional) Create a `.env` file to store configuration:
   ```env
   OPENAI_API_KEY=your_key_here
   DEFAULT_OUTPUT_DIR=summaries  # custom summaries folder
   DEFAULT_VIDEO_DIR=videos      # custom video folder
   ```
   The application reads these values on startup if the file is present.

## Usage

Launch the GUI:

```bash
run_gui.bat              # Windows: auto-detects venv or Conda
python start_gui.py      # Windows: run directly or double-click
python src/gui.py        # any platform
```

The ``start_gui.py`` launcher hides the console window when executed with
``pythonw`` (as done in ``run_gui.bat``). When run directly, it attempts to load
dependencies from a local ``venv`` folder if present. If packages are missing,
use ``run_gui.bat`` or install the requirements into your default Python
environment.

Enter video URLs or select audio files, then run the desired actions to download, transcribe and summarise content.
