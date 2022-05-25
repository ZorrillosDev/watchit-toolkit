from pathlib import Path
from src.core import logger, util
from src.core.media.assets.factory import input, representation, Size, SIZES


def auto_resize_to_default(input_image: str, output: str):
    """
    Resize image and keep their aspect ratios
    :param input_image: Path to image
    :param output: Where store the resized image
    """
    for size in SIZES:
        file_format = util.extract_extension(input_image)
        yield resize_thumbnails(input_image, f"{output}/{size}.{file_format}", size)


# TODO write tests
def resize_thumbnails(input_image: str, output: str, size):
    """
    Resize image and keep their aspect ratios
    :param input_image: Path to image
    :param output: Where store the resized image
    :param size: Size to resize
    """

    # Keep original requested size if `size` is Size subtype
    size_representation = representation(size) if not isinstance(size, Size) else size

    # Avoid pass if invalid representation or not `size` subtype
    if not size_representation and not isinstance(size, Size):
        raise ValueError(
            "Invalid size representation. "
            "Please provide valid one. eg: small, medium, large"
        )
    with input(input_image) as image:

        # Exists path to image and has not default original size
        if Path(output).exists() and image.size == size_representation:
            logger.log.warning(f"Skipping media already processed: {output}")
            return

        logger.log.warn(f"Resizing image {image.size} -> {size_representation}")
        image.thumbnail(size_representation)
        image.save(output)
        return image
