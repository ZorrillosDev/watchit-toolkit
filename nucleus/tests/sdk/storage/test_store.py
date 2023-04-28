import responses
import nucleus.sdk.storage as storage

from nucleus.core.types import Path, JSON
from nucleus.sdk.processing import File
from nucleus.sdk.storage import Object


@responses.activate
def test_storage_file(rpc_api_add_request: JSON, mock_local_video_path: Path):
    """Should dispatch the right request based on storable input"""

    # retrieve the storage node, by default local ipfs local node
    local_node = storage.ipfs()

    # store a new file in local node
    storable = File(path=mock_local_video_path)
    stored = local_node(storable)  # expected Stored output

    output_hash = rpc_api_add_request.get("Hash")
    output_name = rpc_api_add_request.get("Name")
    output_size = int(rpc_api_add_request.get("Size", 0))

    assert stored.hash.valid()
    assert stored.hash == output_hash
    assert stored.name == output_name
    assert stored.size == output_size
    assert isinstance(stored, Object)
