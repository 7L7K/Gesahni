from flask import Flask, request, jsonify, render_template
import logging
import tempfile
import subprocess
from pathlib import Path
import yaml

from src.transcription.base import TranscriptionService

def load_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as exc:
        logger = logging.getLogger(__name__)
        logger.exception("Failed to load config: %s", exc)
        return {}

# ---- Logging setup ----
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ---- Config and Transcriber setup ----
config = load_config("config.yaml")
transcriber = TranscriptionService(config.get("whisper_model", "base"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_route():
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        return jsonify({'error': 'missing file'}), 400

    file = request.files['file']
    logger.info("Received file: %s", file.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = Path(tmpdir) / 'video.webm'
        audio_path = Path(tmpdir) / 'audio.wav'
        try:
            file.save(video_path)
            logger.info("Saved uploaded file to %s", video_path)
            # Convert video to audio using ffmpeg
            subprocess.run(
                ['ffmpeg', '-y', '-i', str(video_path), str(audio_path)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            logger.info("Audio extracted to %s", audio_path)
        except subprocess.CalledProcessError as exc:
            logger.error("ffmpeg failed: %s", exc)
            return jsonify({'error': f'ffmpeg failed: {exc}'}), 500
        except Exception as exc:
            logger.exception("Unexpected error processing file: %s", exc)
            return jsonify({'error': f'Error processing file: {exc}'}), 500

        try:
            text = transcriber.transcribe(str(audio_path))
            logger.info("Transcription complete for %s", file.filename)
        except Exception as exc:
            logger.exception("Transcription failed: %s", exc)
            return jsonify({'error': f'transcription failed: {exc}'}), 500

    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)
