import os
import base64
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception:  # pragma: no cover - optional dependency
    AESGCM = None
try:
    from cryptography.fernet import Fernet
except Exception:  # pragma: no cover - optional dependency
    Fernet = None

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
    return os.urandom(32)

AES_KEY = _load_aes_key()

def encrypt_file(in_path: str, out_path: str) -> None:
    """Encrypt ``in_path`` to ``out_path`` using AES-256-GCM."""
    if AESGCM is None:
        raise RuntimeError("cryptography not available")
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        data = fh.read()
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, data, None)
    with open(out_path, "wb") as fh:
        fh.write(nonce + encrypted)

def decrypt_file(in_path: str, out_path: str) -> None:
    """Decrypt ``in_path`` to ``out_path`` using AES-256-GCM."""
    if AESGCM is None:
        raise RuntimeError("cryptography not available")
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        payload = fh.read()
    nonce, ciphertext = payload[:12], payload[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    with open(out_path, "wb") as fh:
        fh.write(decrypted)

# --- Fernet for BYTES encryption (snippets, database fields, etc) ---

FERNET_KEY = os.getenv("FERNET_KEY")
if Fernet is not None:
    if not FERNET_KEY:
        FERNET_KEY = Fernet.generate_key()
    fernet = Fernet(FERNET_KEY)
else:  # pragma: no cover - cryptography not available
    FERNET_KEY = ""
    class _DummyFernet:
        def encrypt(self, data: bytes) -> bytes:
            return data
        def decrypt(self, data: bytes) -> bytes:
            return data
    fernet = _DummyFernet()

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes using Fernet."""
    return fernet.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes using Fernet."""
    return fernet.decrypt(data)

# TODO: implement a key rotation script that re-encrypts existing files with a
# new key while preserving data integrity.
