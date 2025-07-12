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
- `openai` (for GPT-4 summarization)

## Running the Application

After installing dependencies, you can run the main script with an audio file as input:

```bash
python main.py path/to/audiofile
```

The script will output the transcribed text to the console.

## Configuration

Runtime options are stored in `config.yaml`. The file includes settings for
audio recording parameters, the Whisper model to load, GPT-4 analysis options,
and the directory used for session data. Adjust these values to customize how
the assistant operates.

Key options include:

- `whisper_model` – which Whisper model to load for transcription
- `analysis_model` – GPT-4 model name used for summarization
- `session_root` – directory where session folders are created
- `flask_debug` – enable or disable Flask debug mode

### Web Interface

The project also includes a minimal web interface for recording video with audio.
Run the Flask server and open `http://localhost:5000` in a browser:

```bash
python server.py
```

The page displays the live camera feed with **Start** and **Stop** buttons. After stopping, the recording is offered as `video.webm` for download. You may also send the captured audio to the backend for transcription (if Whisper is installed) using the **Send Audio** button.

Uploaded recordings are stored under `sessions/YYYY-MM-DD/`. Incoming chunks are appended to `video.webm`; once the final clip is sent, the server produces `audio.wav`, appends the transcription to `transcript.txt`, and stores any comma-separated tags into `tags.json`.

### Live Streaming

While recording, the application now uploads short WebM chunks to `/upload`. Each chunk is transcribed on the server and the text is shown live beneath the video element.

### Automatic GPT-4 Analysis

After the full recording is processed, the transcript is analyzed with GPT-4. The
resulting summary is written to `summary.json` inside the session folder. A
separate `status.json` file tracks the state of the current transcription and
analysis.

You can query the latest analysis with:

```bash
curl http://localhost:5000/status/latest
```

Example response:

```json
{
  "transcript": "...", 
  "summary": "Key points and actions",
  "status": "complete"
}
```

## Contribution Guidelines

Contributions are welcome! To contribute:

1. Fork this repository and create a new branch for your change.
2. Make your modifications and include clear commit messages.
3. Open a pull request describing your changes.

Please ensure your code follows standard Python style conventions and includes appropriate documentation.
