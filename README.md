# Gesahni

## Project Goals

Gesahni aims to provide a simple interface for converting audio to text using [Whisper](https://github.com/openai/whisper). The project serves as a starting point for experimenting with speech-to-text workflows in Python.

## Installation

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.

## Dependencies

- Python 3.8 or later
- [Whisper](https://github.com/openai/whisper)
- `ffmpeg` (required by Whisper for audio processing)

## Running the Application

After installing dependencies, run the main script. It will create a session
folder for today's date inside the `sessions/` directory. Place an `audio.wav`
file in that folder and run:

```bash
python main.py
```

The transcription will be stored as `transcript.txt` inside the same session
folder and printed to the console.

## Contribution Guidelines

Contributions are welcome! To contribute:

1. Fork this repository and create a new branch for your change.
2. Make your modifications and include clear commit messages.
3. Open a pull request describing your changes.

Please ensure your code follows standard Python style conventions and includes appropriate documentation.
