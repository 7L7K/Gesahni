import sys
from pathlib import Path

import pytest

# Add repo root to sys.path so tests can import package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.memory.memory import Memory  # noqa: E402


def test_memory_add_and_search(tmp_path, monkeypatch):
    # Ensure the Memory class uses the fallback implementation
    import src.memory.memory as memory_mod
    monkeypatch.setattr(memory_mod, "chromadb", None)
    memory = Memory(persist_directory=str(tmp_path))

    first = "hello world"
    second = "testing memory"
    memory.add(first)
    memory.add(second)

    results = memory.search("hello")
    assert first in results
    assert second in results

