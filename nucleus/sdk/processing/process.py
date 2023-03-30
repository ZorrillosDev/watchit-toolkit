import ffmpeg  # type: ignore
import PIL.Image as PIL

from functools import singledispatch
from nucleus.core.types import Any, Path
from nucleus.sdk.harvest import Video, Image

from .engines import VideoEngine, ImageEngine
from .types import Engine, Processable


@singledispatch
def engine(model: Processable) -> Engine[Any]:
    """Engine single dispatch factory.
    Use the model input to infer the right engine.

    :param model: the model to dispatch
    :param kwargs: these args are passed directly to library.
    :return: engine instance
    :rtype: Engine
    """
    raise NotImplementedError(f"cannot process not registered media `{model}")


@engine.register
def _(model: Video) -> VideoEngine:
    input_path = Path(model.route)
    library = ffmpeg.input(input_path)  # type: ignore
    return VideoEngine(model.type, library)  # type: ignore


@engine.register
def _(model: Image) -> ImageEngine:
    input_path = Path(model.route)
    library = PIL.open(input_path)
    return ImageEngine(model.type, library)


__all__ = ("engine",)