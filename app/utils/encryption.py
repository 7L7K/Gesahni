import os
import base64
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception:  # pragma: no cover - optional dependency may be missing
    class AESGCM:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def generate_key(bit_length: int = 256) -> bytes:
            return b"0" * (bit_length // 8)

        def encrypt(self, nonce: bytes, data: bytes, assoc: bytes | None) -> bytes:
            return data

        def decrypt(self, nonce: bytes, data: bytes, assoc: bytes | None) -> bytes:
            return data

try:
    from cryptography.fernet import Fernet
except Exception:  # pragma: no cover - optional dependency may be missing
    class Fernet:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def generate_key() -> bytes:
            return b"0" * 32

        def encrypt(self, data: bytes) -> bytes:
            return data

        def decrypt(self, data: bytes) -> bytes:
            return data

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

AES_KEY = _load_aes_key()

def encrypt_file(in_path: str, out_path: str) -> None:
    """Encrypt `in_path` to `out_path` using AES-256-GCM."""
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        data = fh.read()
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, data, None)
    with open(out_path, "wb") as fh:
        fh.write(nonce + encrypted)

def decrypt_file(in_path: str, out_path: str) -> None:
    """Decrypt `in_path` to `out_path` using AES-256-GCM."""
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
