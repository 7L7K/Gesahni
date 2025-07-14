from pathlib import Path
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sessions import SessionManager


def test_create_today_session_creates_files(tmp_path):
    manager = SessionManager(tmp_path.as_posix())
    session_dir = Path(manager.create_today_session())
    assert session_dir.is_dir()
    assert session_dir.name == date.today().isoformat()
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


def test_get_latest_session_returns_most_recent(tmp_path):
    manager = SessionManager(tmp_path.as_posix())
    old_dir = tmp_path / "2020-01-01"
    new_dir = tmp_path / "2023-01-01"
    old_dir.mkdir()
    new_dir.mkdir()
    assert manager.get_latest_session() == new_dir.as_posix()
