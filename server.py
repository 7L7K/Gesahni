from flask import Flask, request, jsonify, render_template
import logging
import tempfile
import subprocess
from pathlib import Path

from src.transcription.base import TranscriptionService

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
transcriber = TranscriptionService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_route():
    if 'file' not in request.files:
        return jsonify({'error': 'missing file'}), 400
    file = request.files['file']
    logger.info("Received file %s", file.filename)
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = Path(tmpdir) / 'video.webm'
        audio_path = Path(tmpdir) / 'audio.wav'
        file.save(video_path)
        try:
            subprocess.run(
                ['ffmpeg', '-y', '-i', str(video_path), str(audio_path)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception as exc:
            logger.exception("ffmpeg failed: %s", exc)
            return jsonify({'error': f'ffmpeg failed: {exc}'}), 500
        text = transcriber.transcribe(str(audio_path))
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)
