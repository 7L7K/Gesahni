import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.sessions.manager import SessionManager


def test_session_workflow(tmp_path):
    manager = SessionManager(str(tmp_path))

    session_dir = Path(manager.create_today_session())
    expected_files = [
        "video.webm",
        "audio.wav",
        "transcript.txt",
        "tags.json",
        "status.json",
        "summary.json",
    ]
    for name in expected_files:
        assert (session_dir / name).exists()

    assert manager.get_latest_session() == str(session_dir)

    manager.write_status(str(session_dir), True, False)
    data = json.loads((session_dir / "status.json").read_text())
    assert set(data.keys()) == {"whisper_done", "gpt_done"}
