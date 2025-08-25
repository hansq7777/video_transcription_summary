# Video Transcription Summary

This project downloads videos, extracts audio, generates transcripts using OpenAI Whisper, and summarizes the content. The GUI allows entering one or more video URLs or selecting multiple local audio files (common formats are converted to WAV so Whisper can process them). Each source is transcribed in sequence and written to its own transcript file. By default, audio downloads and transcripts are saved under the `summaries` folder, while full video downloads go to the `videos` folder.

Audio shorter than 15 minutes is transcribed directly. Longer media is split into equal parts of up to 15 minutes each before transcription, and the resulting text is concatenated.

## Installation

1. Install [ffmpeg](https://ffmpeg.org/) on your system.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```env
   OPENAI_API_KEY=your_key_here
   DEFAULT_OUTPUT_DIR=summaries  # Optional custom summaries folder
   DEFAULT_VIDEO_DIR=videos      # Optional custom video folder
   ```
   The application reads these values using [python-dotenv](https://github.com/theskumar/python-dotenv).


## Windows Launcher

The `run_gui.bat` script can launch the GUI without manually activating an environment:

1. If a Conda environment is already active, it is used.
2. Otherwise the script tries to run via a Conda environment named `VTS` (change `CONDA_ENV_NAME` in the script to use a different name).
3. If Conda is unavailable, it falls back to a local `venv` if one exists.

Double-click `run_gui.bat` in the project folder. The script runs `src\gui.py` with `pythonw`, so no console window appears. If no suitable environment is found, it displays instructions for creating one.
