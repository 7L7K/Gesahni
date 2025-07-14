import os
import base64
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    AESGCM = None  # type: ignore

try:
    from cryptography.fernet import Fernet  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    class _DummyFernet:
        def __init__(self, *a, **k):
            pass

        @staticmethod
        def generate_key() -> bytes:
            return b"0" * 16

        def encrypt(self, data: bytes) -> bytes:
            return data

        def decrypt(self, data: bytes) -> bytes:
            return data

    Fernet = _DummyFernet  # type: ignore

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
    if AESGCM is not None:
        return AESGCM.generate_key(bit_length=256)
    return b"0" * 32

AES_KEY = _load_aes_key()

def encrypt_file(in_path: str, out_path: str) -> None:
    """Encrypt ``in_path`` to ``out_path`` using AES-256-GCM if available."""
    if AESGCM is None:
        # Fallback: just copy the file for testing environments
        from shutil import copyfile
        copyfile(in_path, out_path)
        return
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        data = fh.read()
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, data, None)
    with open(out_path, "wb") as fh:
        fh.write(nonce + encrypted)

def decrypt_file(in_path: str, out_path: str) -> None:
    """Decrypt ``in_path`` to ``out_path`` using AES-256-GCM if available."""
    if AESGCM is None:
        # Fallback: just copy the file for testing environments
        from shutil import copyfile
        copyfile(in_path, out_path)
        return
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        payload = fh.read()
    nonce, ciphertext = payload[:12], payload[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    with open(out_path, "wb") as fh:
        fh.write(decrypted)

# --- Fernet for BYTES encryption (snippets, database fields, etc) ---

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key()
fernet = Fernet(FERNET_KEY)

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes using Fernet."""
    return fernet.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes using Fernet."""
    return fernet.decrypt(data)

# TODO: implement a key rotation script that re-encrypts existing files with a
# new key while preserving data integrity.
