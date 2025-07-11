from flask import Flask, request, jsonify, render_template
import tempfile
import subprocess
from pathlib import Path
import yaml

from src.transcription.base import TranscriptionService


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


config = load_config("config.yaml")
transcriber = TranscriptionService(config.get("whisper_model", "base"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_route():
    if 'file' not in request.files:
        return jsonify({'error': 'missing file'}), 400
    file = request.files['file']
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
            return jsonify({'error': f'ffmpeg failed: {exc}'}), 500
        text = transcriber.transcribe(str(audio_path))
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)
