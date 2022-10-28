import pytest
from src.core.image import input, Size
from src.core.exceptions import InvalidImageSize


root_dir = "src/tests/core/fixture/"
image_dir_771 = f"{root_dir}771x900.jpg"
image_dir_255 = f"{root_dir}255x255.jpg"
image_dir_638 = f"{root_dir}638x400.jpg"

def test_sizes():
    """Should contains valid image sizes"""

    assert Size.Small == (45, 67)
    assert Size.Medium == (230, 345)
    assert Size.Large == (500, 750)


def test_valid_input():
    """Should success for valid input image"""
    with input(image_dir_771) as image:
        w, h = image.size
        assert w == 771
        assert h == 900


def test_invalid_255x255_input():
    """Should fail image input 255x255 since is less than master 500x750 size"""

    with pytest.raises(InvalidImageSize):
        with input(image_dir_255):
            ...


def test_invalid_638x400_input():
    """Should fail if image width is larger than height input 638x400 size"""

    with pytest.raises(InvalidImageSize):
        with input(image_dir_638):
            ...