import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


_KEY_ENV = "AES_KEY"


def _load_key() -> bytes:
    key_b64 = os.getenv(_KEY_ENV)
    if key_b64:
        try:
            key = base64.urlsafe_b64decode(key_b64)
        except Exception:
            key = None
        if key and len(key) == 32:
            return key
    # Generate a random key if not provided; useful for development
    return AESGCM.generate_key(bit_length=256)


AES_KEY = _load_key()


def encrypt_file(in_path: str, out_path: str) -> None:
    """Encrypt ``in_path`` to ``out_path`` using AES-256-GCM."""
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        data = fh.read()
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, data, None)
    with open(out_path, "wb") as fh:
        fh.write(nonce + encrypted)


def decrypt_file(in_path: str, out_path: str) -> None:
    """Decrypt ``in_path`` to ``out_path`` using AES-256-GCM."""
    aesgcm = AESGCM(AES_KEY)
    with open(in_path, "rb") as fh:
        payload = fh.read()
    nonce, ciphertext = payload[:12], payload[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    with open(out_path, "wb") as fh:
        fh.write(decrypted)


# TODO: implement a key rotation script that re-encrypts existing files with a
# new key while preserving data integrity.
