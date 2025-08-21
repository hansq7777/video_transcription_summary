# Video Transcription Summary

This project downloads videos, extracts audio, generates transcripts using OpenAI Whisper, and summarizes the content. The GUI allows entering a video URL or selecting a local audio file (common formats are converted to WAV so Whisper can process them).

## Installation

1. Install [ffmpeg](https://ffmpeg.org/) on your system.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```env
   OPENAI_API_KEY=your_key_here
   DEFAULT_OUTPUT_DIR=summaries  # Optional custom folder
   ```
   The application reads these values using [python-dotenv](https://github.com/theskumar/python-dotenv).

