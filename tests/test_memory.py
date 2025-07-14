import sys
from pathlib import Path

import pytest  # Needed for tmp_path and monkeypatch fixtures

# Ensure the repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.memory.memory import Memory  # noqa: E402


def test_memory_add_and_search_fallback(tmp_path, monkeypatch):
    """
    Verify that the fallback (in-memory) implementation works when chromadb
    is unavailable.
    """
    import src.memory.memory as memory_mod  # local import to patch correctly
    monkeypatch.setattr(memory_mod, "chromadb", None)

    mem = Memory(persist_directory=str(tmp_path))

    first = "hello world"
    second = "testing memory"
    mem.add(first)
    mem.add(second)

    results = mem.search("hello")
    assert first in results
    assert second in results


def test_memory_add_and_search_top_k(tmp_path):
    """
    Confirm that top_k limiting works with the default backend.
    """
    mem = Memory(persist_directory=tmp_path.as_posix())
    mem.add("hello world")
    mem.add("another entry")

    results = mem.search("hello", top_k=1)
    assert results == ["hello world"]
