from flask import jsonify, request, Blueprint
from src.sdk.cache import frozen, ingested, aggregated, DESCENDING
from src.sdk.media.metadata import generate_erc1155
from src.sdk.scheme.validator import check
from src.sdk.constants import NODE_URI

cache_ = Blueprint('cache', __name__)


def _clean_internals(entry):
    """
    Re-struct response cleaning internal data
    :param entry: MovieScheme dict
    :return MovieScheme dict with cleaned and sanitized fields
    """

    # Clean not public data
    del entry["properties"]["properties"]["hash"]
    del entry["properties"]["properties"]["resource"]
    # Movie imdb_code to get sanitize URI
    imdb_code = entry["properties"]["properties"]["imdb_code"]
    # Sanitize uri to get handled by proxy
    new_image_path = f"{NODE_URI}/proxy{entry['properties']['image']}?imdb={imdb_code}"
    entry["properties"]["image"] = new_image_path
    return entry


@cache_.route("/recent", methods=["GET"])
def recent():
    order_by = request.args.get("order", DESCENDING)
    limit = request.args.get("limit", 10)

    # Get current latest minted movies
    minted_nft, _ = frozen({}, {"cid": 1, "_id": False})
    meta_data_limited = minted_nft.limit(limit)  # slice response
    mapped_cid = list(map(lambda x: x.get("cid"), meta_data_limited))

    # Parse erc1155 metadata
    # Get "in-relation" hash from ingested metadata
    metadata_for_cid, _ = ingested({"hash": {"$in": mapped_cid}})
    metadata_for_cid.sort([("_id", order_by)])  # sort descending by date

    # Generate metadata ERC1155 for response
    movies_meta = map(generate_erc1155, check(metadata_for_cid))
    movies_meta = map(_clean_internals, movies_meta)
    return jsonify(list(movies_meta))


@cache_.route("/creators", methods=["GET"])
def creators():
    order_by = request.args.get("order", DESCENDING)
    limit = request.args.get("limit", 6)

    # Get current latest minted movies
    aggregation_group = [
        {"$group": {"_id": "$creator", "sum": {"$sum": 1}}},
        {"$limit": limit},
        {"$sort": {"_id": order_by}},
    ]

    recent_minters = aggregated(aggregation_group)
    recent_minters = map(lambda x: {'address': x['_id'], 'movies': x['sum']}, recent_minters)
    return jsonify(list(recent_minters))
