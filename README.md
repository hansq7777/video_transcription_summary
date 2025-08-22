# Video Transcription Summary

This project downloads videos, extracts audio, generates transcripts using OpenAI Whisper, and summarizes the content. The GUI allows entering one or more video URLs or selecting multiple local audio files (common formats are converted to WAV so Whisper can process them). Each source is transcribed in sequence and written to its own transcript file.

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
   DEFAULT_OUTPUT_DIR=summaries  # Optional custom folder
   ```
   The application reads these values using [python-dotenv](https://github.com/theskumar/python-dotenv).

