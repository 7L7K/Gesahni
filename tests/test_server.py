import io
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    server.SESSION_DIR = tmp_path
    def fake_run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        Path(cmd[-1]).write_bytes(b"audio")
        return subprocess.CompletedProcess(cmd, 0, b"", b"")
    monkeypatch.setattr(server.subprocess, "run", fake_run)
    return server.app.test_client()

def test_transcribe_success(client, monkeypatch):
    monkeypatch.setattr(server.transcriber, "transcribe", lambda p: "hello")
    data = {"file": (io.BytesIO(b"data"), "video.webm")}
    resp = client.post("/transcribe", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert resp.get_json() == {"text": "hello"}

def test_upload_success(client, monkeypatch):
    monkeypatch.setattr(server.transcriber, "transcribe", lambda p: "chunk")
    data = {"file": (io.BytesIO(b"data"), "chunk.webm")}
    resp = client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert resp.get_json() == {"text": "chunk"}

def test_status_latest(client, tmp_path):
    text_file = tmp_path / "transcript.txt"
    text_file.write_text("one\ntwo\n", encoding="utf-8")
    server.SESSION_DIR = tmp_path
    resp = client.get("/status/latest")
    assert resp.status_code == 200
    assert resp.get_json() == {"text": "two"}

def test_transcribe_whisper_unavailable(client, monkeypatch):
    monkeypatch.setattr(server.transcriber, "transcribe", lambda p: None)
    data = {"file": (io.BytesIO(b"data"), "video.webm")}
    resp = client.post("/transcribe", data=data, content_type="multipart/form-data")
    assert resp.status_code == 500
    assert "error" in resp.get_json()


def test_chat_route(client, monkeypatch):
    monkeypatch.setattr(server.chatbot, "chat", lambda msg: "hi " + msg)
    resp = client.post("/chat", json={"message": "there"})
    assert resp.status_code == 200
    assert resp.get_json() == {"response": "hi there"}


def test_search_route(client, monkeypatch):
    monkeypatch.setattr(server.memory, "search", lambda q: ["one", "two"])
    resp = client.get("/search?q=hello")
    assert resp.status_code == 200
    assert resp.get_json() == {"results": ["one", "two"]}


def test_handle_chunk_ws(tmp_path, monkeypatch):
    server.SESSION_DIR = tmp_path

    def fake_run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        Path(cmd[-1]).write_bytes(b"audio")
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(server.subprocess, "run", fake_run)
    monkeypatch.setattr(server.transcriber, "transcribe", lambda p: "chunk")
    monkeypatch.setattr(server.memory, "add", lambda t: None)
    monkeypatch.setattr(server.session_manager, "create_today_session", lambda: str(tmp_path))

    client = server.socketio.test_client(server.app)
    client.emit("chunk", b"data")
    received = client.get_received()
    assert any(r["name"] == "transcription" and r["args"][0] == {"text": "chunk"} for r in received)

