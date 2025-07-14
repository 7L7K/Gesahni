from shutil import copyfile


def encrypt_file(src: str, dest: str) -> None:
    """Simple placeholder encryption that copies the file."""
    copyfile(src, dest)

from .encryption import (
    encrypt_file,
    decrypt_file,
    encrypt_bytes,
    decrypt_bytes,
)

__all__ = [
    "encrypt_file",
    "decrypt_file",
    "encrypt_bytes",
    "decrypt_bytes",
]
