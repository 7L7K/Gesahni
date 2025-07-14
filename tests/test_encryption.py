import base64
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest


def _reload_encryption(monkeypatch):
    key = base64.urlsafe_b64encode(b"0" * 32).decode()
    fkey = base64.urlsafe_b64encode(b"1" * 32).decode()
    monkeypatch.setenv("AES_KEY", key)
    monkeypatch.setenv("FERNET_KEY", fkey)
    sys.modules.pop("app.utils.encryption", None)
    sys.modules.pop("cryptography", None)
    sys.modules.pop("cryptography.fernet", None)
    return importlib.import_module("app.utils.encryption")


@pytest.fixture
def encryption_module(monkeypatch):
    return _reload_encryption(monkeypatch)


def test_file_round_trip(tmp_path, encryption_module):
    enc = encryption_module
    original = tmp_path / "data.bin"
    original.write_bytes(b"top secret")
    enc_path = tmp_path / "enc.bin"
    dec_path = tmp_path / "dec.bin"

    enc.encrypt_file(str(original), str(enc_path))
    enc.decrypt_file(str(enc_path), str(dec_path))

    assert dec_path.read_bytes() == b"top secret"


def test_bytes_round_trip(encryption_module):
    enc = encryption_module
    payload = b"byte payload"
    encrypted = enc.encrypt_bytes(payload)
    decrypted = enc.decrypt_bytes(encrypted)
    assert decrypted == payload
