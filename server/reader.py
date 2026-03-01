"""Read files from the filesystem for serving."""


def read_file(path: str) -> bytes | None:
    """Read file at path as raw bytes. Return None on I/O error."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None

