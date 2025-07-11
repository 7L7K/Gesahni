class Memory:
    """Simple in-memory storage."""
    def __init__(self):
        self._data = []

    def add(self, item: str) -> None:
        self._data.append(item)

    def get_all(self):
        return list(self._data)
