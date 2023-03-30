from PIL.Image import Resampling
from dataclasses import dataclass

"""All these settings are defined by pillow library.
Option classes should be named in correspondence to the methods of the Pillow Image object and using the Python class naming convention.
Underneath each class is parsed as a method to setup pillow image object.
ref: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize

eg:
    # after parsing
    class RemapPalette(Option) = image.remap_palette(...)
        ...


"""


@dataclass
class Coord:
    """The Python Imaging Library uses a Cartesian pixel coordinate system
    ref: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
    """

    left: int
    top: int
    right: int
    bottom: int


@dataclass
class Crop:
    """Crop image returns a rectangular region from this image
    ref: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.crop
    """

    box: Coord

    def __iter__(self):
        yield "box", (
            self.box.left,
            self.box.top,
            self.box.right,
            self.box.bottom,
        )


@dataclass
class Resize:
    """Resize image
    ref: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize
    """

    width: int
    height: int

    def __post_init__(self):
        self._size = [self.width, self.height]
        self._box = (0, 0, *self._size)
        self._resample = Resampling.BICUBIC

    def crop(self, box: Coord):
        self._box = (box.left, box.top, box.right, box.bottom)

    def resample(self, resample: Resampling):
        self._resample = resample

    def __iter__(self):
        yield "size", self._size
        yield "resample", self._resample
        yield "box", self._box


__all__ = ("Crop", "Coord", "Resize", "Resampling")