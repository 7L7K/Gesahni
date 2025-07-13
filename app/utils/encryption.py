import os
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(FERNET_KEY)


def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes using Fernet."""
    return fernet.encrypt(data)


def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes using Fernet."""
    return fernet.decrypt(data)
