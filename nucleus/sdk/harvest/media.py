from nucleus.core.types import Path
from .models import Collectable, Media
from .types import MediaType

"""
Each specification defines how media types are processed and stored.
The behavior of media types in the context of processing and storage is defined by each specification.
"""


class File(Media[Path]):
    """Generic local media path.
    This class is used to infer any media stored in local host.
    """

    ...


class Video(Collectable):
    """Video class establishes how the videos should be processed"""

    type = MediaType.VIDEO


class Image(Collectable):
    """Image class establishes how the images should be processed"""

    type = MediaType.IMAGE


__all__ = ("Image", "Video", "File")