import json
from pathlib import Path
import types
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.assistant import gpt_worker
from src.sessions.manager import SessionManager

class DummyResp:
    def __init__(self, content):
        self.choices = [{"message": {"content": content}}]

def make_openai(content):
    class Chat:
        @staticmethod
        def create(**kwargs):
            return {"choices": [{"message": {"content": content}}]}
    return types.SimpleNamespace(ChatCompletion=Chat)

@pytest.fixture
def dummy_manager(monkeypatch):
    mgr = SessionManager()
    monkeypatch.setattr(mgr, "write_status", lambda *a, **k: None)
    return mgr


def test_generate_summary_success(tmp_path, monkeypatch, dummy_manager):
    session = tmp_path / "s1"
    session.mkdir()
    (session / "transcript.txt").write_text("hello world", encoding="utf-8")
    monkeypatch.setattr(gpt_worker, "openai", make_openai("short summary"))
    gpt_worker.generate_summary(session.as_posix(), dummy_manager)
    data = json.loads((session / "summary.json").read_text())
    assert data["summary"] == "short summary"
    assert data["next_question"]


def test_generate_summary_rate_limit(tmp_path, monkeypatch, dummy_manager):
    session = tmp_path / "s1"
    session.mkdir()
    text = "a" * 150
    (session / "transcript.txt").write_text(text, encoding="utf-8")

    class DummyErr(Exception):
        pass

    class Chat:
        @staticmethod
        def create(**kwargs):
            raise DummyErr()

    monkeypatch.setattr(gpt_worker, "openai", types.SimpleNamespace(ChatCompletion=Chat))
    monkeypatch.setattr(gpt_worker, "RateLimitError", DummyErr)
    gpt_worker.generate_summary(session.as_posix(), dummy_manager)
    data = json.loads((session / "summary.json").read_text())
    assert data["summary"] == text[:100]

