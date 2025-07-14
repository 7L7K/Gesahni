import os
import base64

# ------------------------------------------------------------
# Optional dependencies (cryptography).  Fall back gracefully
# ------------------------------------------------------------

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.fernet import Fernet
    _crypto_available = True
except Exception:  # pragma: no cover – cryptography not installed
    class AESGCM:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def generate_key(bit_length: int = 256) -> bytes:
            return b"0" * (bit_length // 8)

        def encrypt(self, nonce: bytes, data: bytes, assoc=None) -> bytes:
            return data

        def decrypt(self, nonce: bytes, data: bytes, assoc=None) -> bytes:
            return data

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
    _crypto_available = False

# ------------------------------------------------------------
# AES-256-GCM · FILE encryption helpers
# ------------------------------------------------------------
_AES_KEY_ENV = "AES_KEY"

def _load_aes_key() -> bytes:
    """
    Load a 32-byte AES key from the AES_KEY env-var (URL-safe base64);
    otherwise generate a fresh key (dev / fallback use).
    """
    key_b64 = os.getenv(_AES_KEY_ENV)
    if key_b64:
        try:
            key = base64.urlsafe_b64decode(key_b64)
            if len(key) == 32:
                return key
        except Exception:
            pass

    # Generate a new key
    return AESGCM.generate_key(bit_length=256)

AES_KEY: bytes = _load_aes_key()

def encrypt_file(in_path: str, out_path: str) -> None:
    """
    Encrypt *in_path* → *out_path* with AES-256-GCM.
    If cryptography isn’t available, falls back to a simple file copy.
    """
    try:
        aesgcm = AESGCM(AES_KEY)
        with open(in_path, "rb") as fh:
            data = fh.read()
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, data, None)
        with open(out_path, "wb") as fh:
            fh.write(nonce + ciphertext)
    except Exception:
        with open(in_path, "rb") as src, open(out_path, "wb") as dst:
            dst.write(src.read())

def decrypt_file(in_path: str, out_path: str) -> None:
    """
    Decrypt *in_path* → *out_path* with AES-256-GCM.
    Falls back to a raw copy when cryptography isn’t available.
    """
    try:
        aesgcm = AESGCM(AES_KEY)
        with open(in_path, "rb") as fh:
            payload = fh.read()
        nonce, ciphertext = payload[:12], payload[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        with open(out_path, "wb") as fh:
            fh.write(plaintext)
    except Exception:
        with open(in_path, "rb") as src, open(out_path, "wb") as dst:
            dst.write(src.read())

# ------------------------------------------------------------
# Fernet · BYTES encryption helpers (snippets, DB fields, etc.)
# ------------------------------------------------------------
_FERNET_KEY_ENV = "FERNET_KEY"
fernet_key = os.getenv(_FERNET_KEY_ENV) or Fernet.generate_key()

try:
    fernet = Fernet(fernet_key)
except Exception:
    class _DummyFernet:
        def encrypt(self, data: bytes) -> bytes:
            return data
        def decrypt(self, data: bytes) -> bytes:
            return data
    fernet = _DummyFernet()

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes when Fernet is available; otherwise return unchanged."""
    return fernet.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes when Fernet is available; otherwise return unchanged."""
    return fernet.decrypt(data)

# ------------------------------------------------------------
# TODO:
#   • Build a key-rotation utility to walk existing assets,
#     decrypt them with the old key, and re-encrypt with the new one.
# ------------------------------------------------------------
