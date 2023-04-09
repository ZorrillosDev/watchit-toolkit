import responses
import nucleus.sdk.storage as storage

from nucleus.core.types import Path, JSON
from nucleus.sdk.harvest import File, MediaType
from nucleus.sdk.storage import Stored


@responses.activate
def test_storage_file(rpc_api_add_request: JSON, mock_local_video_path: Path):
    """Should dispatch the right request based on storable input"""

    # retrieve the storage node, by default local ipfs local node
    local_node = storage.ipfs()

    # store a new file in local node
    storable = File(route=mock_local_video_path, type=MediaType.VIDEO)
    stored = local_node(storable)  # expected Stored output

    assert stored.cid.valid()
    assert stored.cid == "bafyjvzacdjrk37kqvy5hbqepmcraz3txt3igs7dbjwwhlfm3433a"
    assert stored.name == "meta"
    assert stored.size == 202
    assert isinstance(stored, Stored)
