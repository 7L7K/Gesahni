# Gesahni

## Project Goals

Gesahni aims to provide a simple interface for converting audio to text using [Whisper](https://github.com/openai/whisper). The project serves as a starting point for experimenting with speech-to-text workflows in Python.

## Installation

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.

## Dependencies

- Python 3.8 or later
- [Whisper](https://github.com/openai/whisper) (optional for transcription)
- `ffmpeg` (required by Whisper for audio processing)

## Running the Application

After installing dependencies, you can run the main script with an audio file as input:

```bash
python main.py path/to/audiofile
```

The script will output the transcribed text to the console.

## Configuration

Runtime options are stored in `config.yaml`. The file includes settings for
audio recording parameters, the Whisper model to load, and the directory used
for session data. Adjust these values to customize how the assistant operates.

### Web Interface

The project also includes a minimal web interface for recording video with audio.
Run the Flask server and open `http://localhost:5000` in a browser:

```bash
python server.py
```

The page displays the live camera feed with **Start** and **Stop** buttons. After stopping, the recording is offered as `video.webm` for download. You may also send the captured audio to the backend for transcription (if Whisper is installed) using the **Send Audio** button.

## Contribution Guidelines

Contributions are welcome! To contribute:

1. Fork this repository and create a new branch for your change.
2. Make your modifications and include clear commit messages.
3. Open a pull request describing your changes.

Please ensure your code follows standard Python style conventions and includes appropriate documentation.
