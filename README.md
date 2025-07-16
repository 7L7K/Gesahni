# Gesahni

## Project Goals

Gesahni aims to provide a simple interface for converting audio to text using [Whisper](https://github.com/openai/whisper). The project serves as a starting point for experimenting with speech-to-text workflows in Python.

## Installation

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.

## Setup

Docker Compose is provided for local development:

```bash
docker-compose up --build
```

Once running, a Flower dashboard for Celery is available at
`http://localhost:5555`.

The React frontend can be started separately:

```bash
cd frontend && npm install && npm run dev
```

### Environment variables

- `DATABASE_URL` – database connection string
- `CELERY_BROKER` – Redis URL used by Celery
- `CELERY_BACKEND` – result backend for Celery
- `FERNET_KEY` – key used for encrypting uploaded media
- A `db` PostgreSQL container stores persistent data for the API and worker
  services

### How to enroll

1. Start the services with Docker Compose.
2. Open the frontend at http://localhost:5173.
3. Record your voice sample and submit.
4. Capture face images from the webcam.
5. Provide preferences and complete enrollment.

## Dependencies

- Python 3.8 or later
- [Whisper](https://github.com/openai/whisper) (optional for transcription)
- `ffmpeg` (required by Whisper for audio processing)
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) (optional for speaker diarization)
- `chromadb` and `sentence-transformers` for vector search persistence
- `Flask-SocketIO` for real-time streaming
- `openai` (for GPT-4 summarization)

## Running the Application

After installing dependencies, you can run the main script with an audio file as input:

```bash
python main.py path/to/audiofile
```

The script will output the transcribed text to the console.

The FastAPI service exposes `/health` for basic status checks and
Prometheus metrics at `/metrics`.

## Configuration

Runtime options are stored in `config.yaml`. The file includes settings for
audio recording parameters, the Whisper model to load, and the directory used
for session data. Adjust these values to customize how the assistant operates.
Setting `enable_diarization` to `true` will load the pyannote diarization
pipeline so that transcripts include speaker labels.
audio recording parameters, the Whisper model to load, GPT-4 analysis options,
and the directory used for session data. Adjust these values to customize how
the assistant operates.

Key options include:

- `whisper_model` – which Whisper model to load for transcription
- `analysis_model` – GPT-4 model name used for summarization
- `session_root` – directory where session folders are created
- `flask_debug` – enable or disable Flask debug mode
- `database_url` – Postgres connection string

### Web Interface

The project also includes a minimal web interface for recording video with audio. It uses WebSockets to stream audio chunks for live transcription.
Run the Flask server and open `http://localhost:5000` in a browser:

```bash
python server.py
```

The page displays the live camera feed with **Start** and **Stop** buttons. After stopping, the recording is offered as `video.webm` for download. You may also send the captured audio to the backend for transcription (if Whisper is installed) using the **Send Audio** button.

Uploaded recordings are stored under `sessions/YYYY-MM-DD/`. Incoming chunks are appended to `video.webm`; once the final clip is sent, the server produces `audio.wav`, appends the transcription to `transcript.txt`, and stores any comma-separated tags into `tags.json`. When the transcription of the final clip completes, the server emits a `final_transcript` event to the browser.

If diarization is enabled, lines in `transcript.txt` will be prefixed with the detected speaker label.

### Live Streaming

While recording, the application streams short WebM chunks to the server over a WebSocket connection. Each chunk is transcribed server-side and the resulting text is pushed back to the browser in real time, updating the text beneath the video element.

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

### Querying Stored Transcripts

All transcriptions are embedded and stored in a persistent vector database. Run
the Flask server and query previous transcripts using the `/search` endpoint:

```bash
curl "http://localhost:5000/search?q=your+query"
```

The endpoint returns the most similar stored texts as a JSON list.

When diarization is enabled the live transcripts and final `transcript.txt` will include speaker names provided by the diarization model.

### Optional Noise Gate

The web interface offers a **Noise gate** checkbox. When enabled, the audio
stream passes through a Web Audio `DynamicsCompressorNode` configured as a
simple gate before being recorded. No additional libraries are required.

## Contribution Guidelines

Contributions are welcome! To contribute:

1. Fork this repository and create a new branch for your change.
2. Make your modifications and include clear commit messages.
3. Open a pull request describing your changes.

Please ensure your code follows standard Python style conventions and includes appropriate documentation.
