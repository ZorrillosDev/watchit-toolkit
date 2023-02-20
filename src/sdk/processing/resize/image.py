import PIL.Image as PIL

# Convention for importing types
from src.core.types import Path, Any
from .types import Size, Sizes, Input


def check_ratio(image: PIL.Image, max_size: Size = Sizes.Large) -> bool:
    """Validate ratio for image

    :param image: Image to validate
    :return: True if image is valid, False otherwise
    :rtype: bool
    """
    # input ratio size
    w, h = image.size
    # ratio height should be major than width
    is_height_less_than_width = h < w
    # input image is smaller than "master".
    # We need to compare each ratio because we have an unexpected result
    is_input_less_than_master = any(
        x < y for x, y in zip(
            image.size, max_size))
    # Invalid image ratio height should be major than width
    return is_height_less_than_width or is_input_less_than_master


def input(input_image: Path, **options: Any) -> Input:
    """Factory Image

    :param input_image: Path to image
    :return: PIL Image object
    :rtype: Image
    :raises InvalidImageSize: if the image ratio is invalid
    """

    return PIL.open(input_image, **options)
