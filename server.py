from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import logging
import tempfile
import subprocess
from pathlib import Path
import yaml
import json
import atexit
import shutil
import os
from dotenv import load_dotenv

from src.sessions import SessionManager
from src.transcription.base import TranscriptionService
from src.memory.memory import Memory
from src.assistant.chat import ChatAssistant

def load_config(path: str) -> dict:
    """Load YAML configuration and substitute environment variables."""
    env_file = Path(path).with_name(".env")
    load_dotenv(env_file)
    try:
        text = Path(path).read_text(encoding="utf-8")
        text = os.path.expandvars(text)
        return yaml.safe_load(text) or {}
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
transcriber = TranscriptionService(
    config.get("whisper_model", "base"),
    enable_diarization=bool(config.get("enable_diarization", False)),
)
session_manager = SessionManager(config.get("session_root", "sessions"))
memory = Memory()
chatbot = ChatAssistant(model_name="gpt-4o")

# Flask debug mode configuration
FLASK_DEBUG = bool(config.get("flask_debug", False))

TMP_SESSION_CREATED = False
try:
    SESSION_DIR = Path(session_manager.create_today_session())
    logger.info("Session directory ready at %s", SESSION_DIR)
except Exception as exc:
    logger.exception("Failed to prepare session directory: %s", exc)
    SESSION_DIR = Path(tempfile.mkdtemp(prefix="session_"))
    TMP_SESSION_CREATED = True
    logger.info("Temporary session directory created at %s", SESSION_DIR)

def _cleanup_tmpdir() -> None:
    if TMP_SESSION_CREATED:
        try:
            shutil.rmtree(SESSION_DIR)
            logger.info("Removed temporary session directory %s", SESSION_DIR)
        except Exception as exc:
            logger.warning("Failed to remove temporary session directory %s: %s", SESSION_DIR, exc)

atexit.register(_cleanup_tmpdir)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search_route():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "missing query"}), 400
    try:
        results = memory.search(query)
    except Exception as exc:
        logger.exception("Search failed: %s", exc)
        return jsonify({"error": f"search failed: {exc}"}), 500
    return jsonify({"results": results})

@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    global SESSION_DIR
    try:
        new_path = Path(session_manager.create_today_session())
        if new_path != SESSION_DIR:
            SESSION_DIR = new_path
    except Exception as exc:
        logger.exception("Failed to ensure session directory: %s", exc)

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
        try:
            memory.add(text)
        except Exception as exc:
            logger.warning("Failed to store transcript in memory: %s", exc)
        socketio.emit("final_transcript", {"text": text})

        if tags:
            try:
                if tags_path.exists():
                    existing = json.loads(tags_path.read_text(encoding="utf-8") or "[]")
                else:
                    existing = []
            except Exception:
                existing = []
            new_tags = [t.strip() for t in tags.split(",") if t.strip()]
            if new_tags:
                existing.extend(new_tags)
                tags_path.write_text(json.dumps(existing), encoding="utf-8")
        # Mark Whisper transcription as done
        session_manager.write_status(str(SESSION_DIR), True, False)
    except Exception as exc:
        logger.exception("Transcription failed: %s", exc)
        return jsonify({"error": f"transcription failed: {exc}"}), 500

    return jsonify({"text": text})


@app.route("/upload", methods=["POST"])
def upload_route():
    """Upload a short video chunk and return its transcription."""
    if "file" not in request.files:
        return jsonify({"error": "missing file"}), 400

    file = request.files["file"]
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = Path(tmpdir) / file.filename
        audio_path = Path(tmpdir) / "audio.wav"
        file.save(video_path)
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(video_path), str(audio_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            logger.exception("ffmpeg failed: %s", exc)
            return jsonify({"error": f"ffmpeg failed: {exc}"}), 500

        text = transcriber.transcribe(str(audio_path))
        if text is None:
            return jsonify({"error": "transcription failed"}), 500
    return jsonify({"text": text})


@app.route("/chat", methods=["POST"])
def chat_route():
    """Respond to a chat message using the language model."""
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not message:
        return jsonify({"error": "missing message"}), 400
    try:
        reply = chatbot.chat(message)
    except Exception as exc:
        logger.exception("Chat failed: %s", exc)
        return jsonify({"error": f"chat failed: {exc}"}), 500
    return jsonify({"response": reply})


@socketio.on("chunk")
def handle_chunk(data: bytes) -> None:
    """Process a streaming video chunk sent over WebSocket."""
    global SESSION_DIR
    try:
        new_path = Path(session_manager.create_today_session())
        if new_path != SESSION_DIR:
            SESSION_DIR = new_path
    except Exception as exc:
        logger.exception("Failed to ensure session directory: %s", exc)

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
            emit("transcription", {"error": str(exc)})
            return
        try:
            text = transcriber.transcribe(str(audio_path))
            if text is None:
                raise RuntimeError("transcription returned None")
            try:
                memory.add(text)
            except Exception as exc:
                logger.warning("Failed to store transcript in memory: %s", exc)
        except Exception as exc:
            logger.exception("Chunk transcription failed: %s", exc)
            emit("transcription", {"error": str(exc)})
            return
    emit("transcription", {"text": text})


@app.route("/status/latest", methods=["GET"])
def latest_status():
    """Return the most recent line of the current transcript."""
    transcript_path = SESSION_DIR / "transcript.txt"
    text = ""
    try:
        if transcript_path.exists():
            lines = transcript_path.read_text(encoding="utf-8").splitlines()
            if lines:
                text = lines[-1]
    except Exception as exc:
        logger.exception("Failed to read transcript: %s", exc)
        return jsonify({"error": f"failed to read transcript: {exc}"}), 500
    return jsonify({"text": text})

@app.route("/status/last-line", methods=["GET"])
def status_last_line():
    """Return the most recent line of transcription."""
    transcript_path = SESSION_DIR / "transcript.txt"
    text = ""
    try:
        if transcript_path.exists():
            lines = transcript_path.read_text(encoding="utf-8").splitlines()
            if lines:
                text = lines[-1]
    except Exception as exc:
        logger.exception("Failed to read transcript: %s", exc)
        return jsonify({"error": f"failed to read transcript: {exc}"}), 500
    return jsonify({"text": text})

if __name__ == "__main__":
    socketio.run(app, debug=FLASK_DEBUG)
