from pathlib import Path


def encrypt_file(src: str, dest: str) -> None:
    """Dummy encrypt by copying ``src`` to ``dest``."""
    Path(dest).write_bytes(Path(src).read_bytes())


def decrypt_file(src: str, dest: str) -> None:
    """Dummy decrypt by copying ``src`` to ``dest``."""
    Path(dest).write_bytes(Path(src).read_bytes())
