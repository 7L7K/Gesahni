import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet

# --- AES-256-GCM for FILE encryption ---
_AES_KEY_ENV = "AES_KEY"

def _load_aes_key() -> bytes:
    key_b64 = os.getenv(_AES_KEY_ENV)
    if key_b64:
        try:
            key = base64.urlsafe_b64decode(key_b64)
        except Exception:
            key = None
        if key and len(key) == 32:
            return key
    # Generate a random key if not provided; useful for development
    return AESGCM.generate_key(bit_length=256)

try:
    AES_KEY = _load_aes_key()
    _aesgcm_available = True
except ImportError:
    AES_KEY = b""
    _aesgcm_available = False

def encrypt_file(in_path: str, out_path: str) -> None:
    """Encrypt `in_path` → `out_path` using AES-256-GCM; falls back to copy if unavailable."""
    if not _aesgcm_available:
        with open(in_path, "rb") as src, open(out_path, "wb") as dest:
            dest.write(src.read())
        return

    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        data = fh.read()
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    with open(out_path, "wb") as fh:
        fh.write(nonce + ciphertext)

def decrypt_file(in_path: str, out_path: str) -> None:
    """Decrypt `in_path` → `out_path` using AES-256-GCM; falls back to copy if unavailable."""
    if not _aesgcm_available:
        with open(in_path, "rb") as src, open(out_path, "wb") as dest:
            dest.write(src.read())
        return

    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        payload = fh.read()
    nonce, ciphertext = payload[:12], payload[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    with open(out_path, "wb") as fh:
        fh.write(plaintext)

# --- Fernet for BYTES encryption (snippets, DB fields, etc.) ---
_FERNET_KEY_ENV = "FERNET_KEY"
fernet_key = os.getenv(_FERNET_KEY_ENV)
if not fernet_key:
    # generate and (optionally) log or persist for later decryptions
    fernet_key = Fernet.generate_key()
    # e.g. print("Generated new FERNET_KEY:", fernet_key)

try:
    fernet = Fernet(fernet_key)
except Exception:
    # cryptography not available or invalid key
    class _DummyFernet:
        def encrypt(self, data: bytes) -> bytes:
            return data
        def decrypt(self, data: bytes) -> bytes:
            return data
    fernet = _DummyFernet()

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes using Fernet when available."""
    return fernet.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes using Fernet when available."""
    return fernet.decrypt(data)

# TODO: implement a key-rotation script that re-encrypts existing files with a
# new key while preserving data integrity.
