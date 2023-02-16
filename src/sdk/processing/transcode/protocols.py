import datetime
import src.sdk.logger as logger

# Convention for importing types
from src.core.types import Sequence, Any, Path
from .types import Streaming, Representation, Formats, Input


def _output(_, duration: int, time_: int, time_left: int):
    """Render tqdm progress bar."""
    per = round(time_ / duration * 100)
    logger.console.status(
        "\rTranscoding...(%s%%) %s left [%s%s]"
        % (
            per,
            datetime.timedelta(seconds=int(time_left)),
            "#" * per,
            "-" * (100 - per),
        )
    )


class HLS(Streaming):
    def __init__(self, input: Input, **kwargs: Any):
        self._hls = input.get_media().hls(self.codec, **kwargs)  # type: ignore
        self._hls.auto_generate_representations()

    def set_representations(self, repr: Sequence[Representation]):
        self._hls.representations(*repr)

    @property
    def codec(self):
        return Formats.h264()  # type: ignore

    def transcode(self, output_dir: Path):
        self._hls.output(output_dir, monitor=_output)


class DASH(Streaming):
    def __init__(self, input: Input, **kwargs: Any):
        self._dash = input.get_media().dash(self.codec, **kwargs)  # type: ignore
        self._dash.auto_generate_representations()

    def set_representations(self, repr: Sequence[Representation]):
        self._dash.representations(*repr)

    @property
    def codec(self):
        return Formats.vp9()  # type: ignore

    def transcode(self, output_dir: Path):
        self._dash.output(output_dir, monitor=_output)