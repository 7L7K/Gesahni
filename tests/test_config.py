import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import load_config


def test_env_substitution(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    cfg_file = tmp_path / "config.yaml"
    env_file.write_text("DATABASE_URL=sqlite:///test.db\n", encoding="utf-8")
    cfg_file.write_text("db_url: ${DATABASE_URL}\n", encoding="utf-8")

    monkeypatch.delenv("DATABASE_URL", raising=False)
    cfg = load_config(str(cfg_file))
    assert cfg["db_url"] == "sqlite:///test.db"
