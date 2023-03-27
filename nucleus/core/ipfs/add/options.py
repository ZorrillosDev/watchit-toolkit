import nucleus.core.exceptions as exceptions

from dataclasses import dataclass
from nucleus.core.types import Path


@dataclass
class File:
    """File represent "files" params in request based on input path.
    :raises exceptions.IPFSRuntimeError if file does not exist.
    """

    path: Path

    def __post_init__(self):
        if not self.path.exists():
            raise exceptions.IPFSRuntimeError(
                f"raised trying to execute `add` directory with an invalid path {self.path}"
            )

    def __iter__(self):
        file_name = self.path.name
        blob = self.path.read_bytes()
        yield "files", {"file": (file_name, blob)}


@dataclass
class Text:
    """Text represent "data" param in request based on input text."""

    input: str

    def __iter__(self):
        yield "data", self.input


__all__ = ("File", "Text")
