import pytest

from src.core.types import Any
from src.sdk.harvest import Codex

from src.tests._mock.models import Movie


@pytest.fixture
def mock_raw_media():
    return {
        "route": "src/tests/_mock/files/watchit.png",
        "type": "image",
    }


@pytest.fixture
def mock_raw_entry():
    """Fixture to provide a mocking for movie"""

    return {
        "title": "A Fork in the Road",
        "imdb_code": "wtt00000000",
        "creator_key": "0xee99ceff640d37edd9cac8c7cff4ed4cd609f435",
        "mpa_rating": "PG",
        "rating": 6.0,
        "runtime": 105.0,
        "synopsis": "Baby loves have fun",
        "release_year": 2010,
        "genres": ["Action", "Comedy", "Crime"],
        "speech_language": "en",
        "publish_date": 1669911990.9270618,
    }


@pytest.fixture
def mock_models(mock_raw_entry: Any, mock_raw_media: Any):
    annotated_model = Codex.annotate(metadata=Movie)
    return annotated_model.parse_obj(
        {"metadata": mock_raw_entry, "media": [mock_raw_media]}
    )
