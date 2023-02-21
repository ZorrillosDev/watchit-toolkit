from functools import singledispatch

from src.core.types import Path
from src.sdk.harvest import Video, Image, Stream
from src.sdk.harvest.model import Media

from .engines import VideoEngine, ImageEngine, StreamEngine
from .types import Engine


@singledispatch
def process(model: Media) -> Engine:
    raise NotImplementedError()


@process.register
def _(model: Video) -> VideoEngine:
    route = Path(str(model.route))
    return VideoEngine(route)


@process.register
def _(model: Stream) -> StreamEngine:
    route = Path(str(model.route))
    return StreamEngine(route)


@process.register
def _(model: Image) -> ImageEngine:
    route = Path(str(model.route))
    return ImageEngine(route)