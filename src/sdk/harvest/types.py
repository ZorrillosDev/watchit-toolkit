"""
Scheme definition for movies. 
Each scheme here defined help us to keep a standard for runtime processing of movies. 
All processed data is later used in the creation of standard metadata (ERC-1155, ..), pipeline cache, marshalling, etc; 
"""
import enum
import sqlite3
import pydantic
import src.core.cache as cache

# Convention for importing constants/types
from abc import ABCMeta, abstractmethod
from src.core.types import Any, Iterator, Protocol, Dict
from src.core.cache.types import Cursor, Connection
from .constants import INSERT_MOVIE, FETCH_MOVIE


class MediaType(enum.Enum):
    """Any resource type should be listed here"""

    IMAGE = 0
    VIDEO = 1


class Collector(Protocol, metaclass=ABCMeta):
    """Collector define the methods needed to handle metadata collection process"""

    def __str__(self) -> str:
        """Context name for current data.

        We use this context name to keep a reference to data.
        """
        return "__collectable__"

    @abstractmethod
    def __iter__(self) -> Iterator[Dict[Any, Any]]:
        """Call could implemented any logic to collect metadata from any kind of data input.

        eg:

        with open("file.json") as file:
            # read movies from json file
            movies = json.load(file)

            for meta in movies:
                yield Movies(**meta)

        """
        ...


class CoreModel(pydantic.BaseModel):
    """Model based SQL manager"""

    class Config:
        conn: Connection | None = None
        query: str = FETCH_MOVIE
        mutation: str = INSERT_MOVIE
        use_enum_values = True
        validate_assignment = True

    def __conform__(self, protocol: sqlite3.PrepareProtocol):
        """Sqlite3 adapter
        ref: https://docs.python.org/3/library/sqlite3.html#sqlite3-adapters
        """
        if protocol is sqlite3.PrepareProtocol:
            raw_fields = self.dict().values()
            map_fields = map(str, raw_fields)
            return ";".join(map_fields)

    @classmethod
    def _get_connection(cls) -> Connection:
        """Singleton connection factory

        :return: connection to use during operations
        :rtype: Connections
        """

        if cls.Config.conn is None:
            cls.Config.conn = cache.connect()
        return cls.Config.conn

    @classmethod
    def get(cls) -> Any:
        """Exec query and fetch one entry from database.

        :return: Any derived model
        :rtype: Any
        """

        conn = cls._get_connection()
        response = conn.execute(cls.Config.query)
        rows = response.fetchone()  # raw data
        return rows[0]

    @classmethod
    def all(cls) -> Iterator[Any]:
        """Exec query and fetch a list of data from database.

        :return: Any list of derived model
        :rtype: Iterator[Any]
        """

        conn = cls._get_connection()
        response = conn.execute(cls.Config.query)
        rows = response.fetchall()  # raw data
        return rows[0]

    def save(self) -> bool:
        """Exec insertion into database using built query

        :return: True if query was saved or False otherwise
        :rtype: bool
        """

        conn = self._get_connection()
        # q: Query = self.Config.query
        cursor: Cursor = conn.execute(self.Config.mutation, (self,))
        return cursor.rowcount > 0