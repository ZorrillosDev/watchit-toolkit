import os
import re
import pytest
from src.core.types import Path

custom_dir = "src/tests/core"
directory = Path("_mock")
image = Path(f"{directory}/watchit.png")
license = Path("LICENSE")
invalid = Path("NOT_EXIST")


def test_valid_read_file():
    """Should return a valid file content with valid directory"""
    with license.read() as content:
        pattern = "GNU AFFERO GENERAL PUBLIC LICENSE"
        assert content is not None
        assert re.search(pattern, content)


def test_invalid_read_file():
    """Should raise FileNotFoundError exception with invalid directory"""
    with pytest.raises(FileNotFoundError):
        with invalid.read():
            ...


# Unit tests
def test_exists_file():
    """Should return True for valid path"""
    existing_file = license.exists()
    assert existing_file is True


# Unit tests
def test_exists_invalid_file():
    """Should return False for invalid path"""
    existing_file = invalid.exists()
    assert existing_file is False


def test_make_destination_dir():
    """Should create directory"""
    new_dir = Path("assets/mock_test_dir/")
    new_created_dir = new_dir.make()
    expected_new_path = Path(new_created_dir)
    assert expected_new_path.exists()
    os.rmdir(new_created_dir)


def test_extract_extension_for_file():
    """Should extract extension from file path"""
    expected = "png"
    provided = Path("watchit.png")
    assert provided.extension() == expected
    assert image.extension() == expected
