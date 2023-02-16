from abc import ABCMeta, abstractmethod
from src.core.types import (
    Sequence,
    TypedDict,
    Any,
    Optional,
    Mapping,
    Iterator,
    Protocol,
    Tuple,
    URL,
    NamedTuple,
    NewType,
)


class Service(TypedDict):
    name: str  # Service name. eg. pinata, filebase.
    endpoint: URL  # api endpoint provided by service
    key: Optional[str]  # auth key provided by service


class DagLink(TypedDict):
    name: Optional[str]
    hash: Mapping[str, str]
    tsize: int


class Dag(TypedDict):
    data: Mapping[str, Mapping[str, str]]
    links: Iterator[DagLink]


# Result type contains standardize output for ipfs commands.
# An issue here is that ipfs returns different encodings for each command, sometimes could be a string and later probably we get a json object,
# so using "output" could be fine to expect always the same field to process.
# eg. call.output
# ref: docs.ipfs.io/reference/cli/#ipfs
ID = NewType("ID", str)
Result = NamedTuple("Result", output=Any)
Services = TypedDict("Services", remote=Iterator[Service])
LocalPin = TypedDict("Pin", pins=Sequence[str])
RemotePin = TypedDict("RemotePin", cid=str, status=str, name=str)


class Container(Protocol, metaclass=ABCMeta):
    """Docker container abstraction adapted from docker lib"""

    @abstractmethod
    def exec_run(self, cmd: str) -> Tuple[bool, bytes]:
        ...
