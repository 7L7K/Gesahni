import os
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(FERNET_KEY)


def encrypt_file(src: str, dest: str) -> None:
    with open(src, "rb") as fh:
        data = fh.read()
    encrypted = fernet.encrypt(data)
    with open(dest, "wb") as fh:
        fh.write(encrypted)


def decrypt_file(src: str, dest: str) -> None:
    with open(src, "rb") as fh:
        data = fh.read()
    decrypted = fernet.decrypt(data)
    with open(dest, "wb") as fh:
        fh.write(decrypted)
