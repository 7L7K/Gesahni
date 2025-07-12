Gesahni

Project Goals
Gesahni provides a simple interface for converting audio to text using Whisper. It's designed as a starting point for experimenting with speech-to-text workflows in Python — with local session logging, optional tagging, and a minimal web interface.
Installation
Clone this repository.
Create and activate a Python virtual environment.
Install dependencies:
pip install -r requirements.txt
Dependencies
Python 3.8 or later
ffmpeg — required for audio extraction
OpenAI Whisper — required for transcription (optional but recommended)
Running the Application (CLI)
After installing dependencies, run the main script with an audio file:
python main.py path/to/audio.wav
This will:
Create a session folder in sessions/YYYY-MM-DD/
Transcribe the file with Whisper
Save the text in transcript.txt and print it to the console
Configuration
Runtime settings live in config.yaml, including:
Whisper model selection (base, medium, etc.)
Session directory path
Debug and logging options
Web Interface
Gesahni also includes a minimal browser-based recording and transcription tool.
To launch it:
python server.py
Then open http://localhost:5000 in your browser.
Features
Webcam + mic recording via MediaRecorder
Start/Stop buttons to control capture
Live preview
Upload to backend for audio extraction and transcription
Upload Workflow
Incoming chunks are saved to sessions/YYYY-MM-DD/video.webm
After the final clip:
audio.wav is extracted
Whisper transcribes the audio → transcript.txt
Any provided tags → tags.json
Live Streaming Transcription
While recording, short WebM chunks are uploaded to /upload.
Each chunk is transcribed on the server
Live captions appear beneath the video in real time
Session Status API
When processing finishes:
The server writes status.json with:
{
  "whisper_done": true,
  "gpt_done": false
}
A background worker (optional) can then:
Summarize the transcript → summary.json
Update the status file to:
{
  "whisper_done": true,
  "gpt_done": true
}
Check /status/latest for:
Transcription status
Generated summary (if available)
Suggested follow-up question
Running Tests
To run unit tests:
pytest
Tests use Flask’s built-in test client to validate core behavior.
Contribution Guidelines
Contributions welcome!
Fork this repo and make a new branch.
Make your changes with clear, descriptive commits.
Open a pull request summarizing your updates.
Please follow standard Python style (PEP8) and include helpful documentation where needed.