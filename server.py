from flask import Flask, request, jsonify, render_template
import logging
import tempfile
import subprocess
from pathlib import Path
import yaml
import json

from src.sessions import SessionManager

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
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---- Config and Transcriber setup ----
config = load_config("config.yaml")
transcriber = TranscriptionService(config.get("whisper_model", "base"))
session_manager = SessionManager(config.get("session_root", "sessions"))
try:
    SESSION_DIR = Path(session_manager.create_today_session())
    logger.info("Session directory ready at %s", SESSION_DIR)
except Exception as exc:
    logger.exception("Failed to prepare session directory: %s", exc)
    SESSION_DIR = Path(tempfile.mkdtemp(prefix="session_"))

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    if "file" not in request.files:
        logger.warning("No file provided in request")
        return jsonify({"error": "missing file"}), 400

    file = request.files["file"]
    logger.info("Received file: %s", file.filename)

    video_path = SESSION_DIR / "video.webm"
    audio_path = SESSION_DIR / "audio.wav"
    transcript_path = SESSION_DIR / "transcript.txt"
    tags_path = SESSION_DIR / "tags.json"
    tags = request.form.get("tags", "")

    try:
        data = file.read()
        with open(video_path, "wb") as dest:
            dest.write(data)
        logger.info("Saved final video to %s", video_path)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path), str(audio_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("Audio extracted to %s", audio_path)
    except subprocess.CalledProcessError as exc:
        logger.error("ffmpeg failed: %s", exc)
        return jsonify({"error": f"ffmpeg failed: {exc}"}), 500
    except Exception as exc:
        logger.exception("Unexpected error processing file: %s", exc)
        return jsonify({"error": f"Error processing file: {exc}"}), 500

    try:
        text = transcriber.transcribe(str(audio_path))
        if text is None:
            raise RuntimeError("transcription returned None")
        with open(transcript_path, "a", encoding="utf-8") as tf:
            tf.write(text + "\n")
        logger.info("Transcription complete for %s", file.filename)

        if tags:
            try:
                if tags_path.exists():
                    existing = json.loads(
                        tags_path.read_text(encoding="utf-8") or "[]"
                    )
                else:
                    existing = []
            except Exception:
                existing = []
            new_tags = [t.strip() for t in tags.split(",") if t.strip()]
            if new_tags:
                existing.extend(new_tags)
                tags_path.write_text(json.dumps(existing), encoding="utf-8")
    except Exception as exc:
        logger.exception("Transcription failed: %s", exc)
        return jsonify({"error": f"transcription failed: {exc}"}), 500

    return jsonify({"text": text})


@app.route("/upload", methods=["POST"])
def upload_chunk():
    """Handle streaming WebM chunks from the browser."""
    if "file" not in request.files:
        logger.warning("No file provided in chunk upload")
        return jsonify({"error": "missing file"}), 400

    file = request.files["file"]
    logger.info("Received chunk %s", file.filename)

    data = file.read()
    session_video = SESSION_DIR / "video.webm"
    try:
        with open(session_video, "ab") as dest:
            dest.write(data)
    except Exception as exc:
        logger.exception("Failed to write chunk to %s: %s", session_video, exc)

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = Path(tmpdir) / "chunk.webm"
        audio_path = Path(tmpdir) / "chunk.wav"
        with open(video_path, "wb") as fh:
            fh.write(data)
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(video_path), str(audio_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            logger.exception("Failed to process chunk: %s", exc)
            return jsonify({"error": f"processing failed: {exc}"}), 500

        try:
            text = transcriber.transcribe(str(audio_path))
            if text is None:
                raise RuntimeError("transcription returned None")
        except Exception as exc:
            logger.exception("Chunk transcription failed: %s", exc)
            return jsonify({"error": f"transcription failed: {exc}"}), 500

    return jsonify({"text": text})


if __name__ == "__main__":
    app.run(debug=True)
