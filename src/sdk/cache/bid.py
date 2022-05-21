from src.core.cache import bid_db
from src.core.cache.manager import retrieve, flush as flusher
from datetime import datetime


def freeze(account: str, bid: str, movie: str) -> dict:
    """
    Insert into cache bid for movie
    :param account: Bidder
    :param bid: Bid amount
    :param movie: Movie id
    """
    zipped = {
        "bid": bid,
        "movie": movie,
        "account": account,
        "created_at": datetime.now(),
    }

    bid_db.movies.insert({**zipped})
    return zipped


def frozen(_filter: dict = None, _opts: dict = None):
    """
    Return bids for movie
    :param _filter: filter dic
    :param _opts: opts dic
    :return: Cursor
    """
    return retrieve(bid_db, _filter, _opts)


def flush(_filter: dict = None):
    """
    Flush bids for specified _filter
    :param _filter: filter dict
    """
    flusher(bid_db, _filter)
    return _filter
