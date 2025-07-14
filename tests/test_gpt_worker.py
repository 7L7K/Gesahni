import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.assistant.gpt_worker import generate_summary
from src.sessions import SessionManager


def test_generate_summary(tmp_path, monkeypatch):
    session_dir = tmp_path / "sess"
    session_dir.mkdir()
    transcript = session_dir / "transcript.txt"
    transcript.write_text("hello there", encoding="utf-8")

    manager = SessionManager(tmp_path.as_posix())
    called = {}

    def fake_write_status(sdir, whisper_done, gpt_done):
        called["args"] = (sdir, whisper_done, gpt_done)

    monkeypatch.setattr(manager, "write_status", fake_write_status)

    generate_summary(session_dir.as_posix(), manager)

    summary_file = session_dir / "summary.json"
    assert summary_file.exists()
    data = json.loads(summary_file.read_text(encoding="utf-8"))
    assert "summary" in data
    assert called.get("args") == (session_dir.as_posix(), True, True)
