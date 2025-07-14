import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import types
import builtins

from app.utils import tts


def test_generate_creates_file(tmp_path, monkeypatch):
    saved = {}

    class DummyTTS:
        def __init__(self, text: str, lang: str = "en") -> None:
            saved["text"] = text
            saved["lang"] = lang

        def save(self, filename: str) -> None:
            saved["path"] = filename
            Path(filename).write_text("data")

    monkeypatch.setattr(tts, "gTTS", DummyTTS)

    out = tmp_path / "out.mp3"
    tts.generate("hello", out.as_posix())

    assert out.exists()
    assert saved.get("path") == out.as_posix()
