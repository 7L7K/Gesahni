from shutil import copyfile


def encrypt_file(src: str, dest: str) -> None:
    """Simple placeholder encryption that copies the file."""
    copyfile(src, dest)

