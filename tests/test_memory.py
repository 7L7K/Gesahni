from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.memory.memory import Memory


def test_memory_add_and_search(tmp_path):
    mem = Memory(persist_directory=tmp_path.as_posix())
    mem.add("hello world")
    mem.add("another entry")
    results = mem.search("hello", top_k=1)
    assert results == ["hello world"]
