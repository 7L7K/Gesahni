import os
import base64

# ------------------------------------------------------------
# Optional dependencies (cryptography).  Fall back gracefully
# ------------------------------------------------------------
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.fernet import Fernet
    _crypto_available = True
except Exception:                  # pragma: no cover – cryptography not installed
    AESGCM = None
    Fernet = None
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
    if _crypto_available:
        return AESGCM.generate_key(bit_length=256)
    return os.urandom(32)


AES_KEY: bytes = _load_aes_key()


def encrypt_file(in_path: str, out_path: str) -> None:
    """
    Encrypt *in_path* → *out_path* with AES-256-GCM.
    If cryptography isn’t available, falls back to a simple file copy.
    """
    if not _crypto_available:
        with open(in_path, "rb") as src, open(out_path, "wb") as dst:
            dst.write(src.read())
        return

    aesgcm = AESGCM(AES_KEY)

    with open(in_path, "rb") as fh:
        data = fh.read()

    nonce = os.urandom(12)              # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, data, None)

    with open(out_path, "wb") as fh:
        fh.write(nonce + ciphertext)


def decrypt_file(in_path: str, out_path: str) -> None:
    """
    Decrypt *in_path* → *out_path* with AES-256-GCM.
    Falls back to a raw copy when cryptography isn’t available.
    """
    if not _crypto_available:
        with open(in_path, "rb") as src, open(out_path, "wb") as dst:
            dst.write(src.read())
        return

    aesgcm = AESGCM(AES_KEY)

    with open(in_path, "rb") as fh:
        payload = fh.read()

    nonce, ciphertext = payload[:12], payload[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    with open(out_path, "wb") as fh:
        fh.write(plaintext)

# ------------------------------------------------------------
# Fernet · BYTES encryption helpers (snippets, DB fields, etc.)
# ------------------------------------------------------------
_FERNET_KEY_ENV = "FERNET_KEY"
fernet_key = os.getenv(_FERNET_KEY_ENV) or (
    Fernet.generate_key() if _crypto_available else None
)

if _crypto_available:
    fernet = Fernet(fernet_key)  # type: ignore[arg-type]
else:
    class _DummyFernet:
        """No-op replacement when cryptography is missing."""
        def encrypt(self, data: bytes) -> bytes:  # pylint: disable=no-self-use
            return data
        def decrypt(self, data: bytes) -> bytes:  # pylint: disable=no-self-use
            return data
    fernet = _DummyFernet()


def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes when Fernet is available; otherwise return unchanged."""
    return fernet.encrypt(data)  # type: ignore[attr-defined]


def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes when Fernet is available; otherwise return unchanged."""
    return fernet.decrypt(data)  # type: ignore[attr-defined]

# ------------------------------------------------------------
# TODO:
#   • Build a key-rotation utility to walk existing assets,
#     decrypt them with the old key, and re-encrypt with the new one.
# ------------------------------------------------------------
