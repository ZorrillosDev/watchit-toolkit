from __future__ import annotations


import pydantic
import ast

# Convention for importing constants/types
from abc import ABC, abstractmethod
from src.core.types import Any, Iterator, Union, List, Path, URL, CID
from .model import Model


class Meta(Model):
    """Abstract metadata model"""

    class Config:
        use_enum_values = True
        validate_assignment = True


class Media(Model):
    """Media define needed field for the multimedia assets schema.    
    All derived class are used as types for dispatch actions.
    eg.
    
        class Video(Media):
            type: Literal["video"] = "video"
        
        
        @singledispatch
        def process(model: Media):
            raise NotImplementedError()
        
        @process.register
        def _(model: Video):
            ...
        
        process(video)    
    """

    route: Union[URL, CID, Path]
    type: str

    @pydantic.validator("route")
    def valid_route(cls, v: str):
        is_url = URL(v).valid()
        is_cid = CID(v).valid()
        is_path = Path(v).is_file()

        if not is_url and not is_path and not is_cid:
            raise ValueError("Route must be a CID | URI | Path")

        return v


class Collection(Model):

    media: List[Media]
    metadata: Meta

    @pydantic.validator("media", pre=True)
    def serialize_media_pre(cls, v: Any):
        """Pre serialize media to object"""
        if isinstance(v, bytes):
            parsed = ast.literal_eval(v.decode())
            instances = map(lambda x: Media(**x), parsed)
            return list(instances)
        return v


class Collector(ABC):
    """Abstract class for collecting metadata.
    Collector define an "strict abstraction" with methods needed to handle metadata collection process.
    Subclasses should implement the __iter__ method to collect metadata from various data inputs.
    """

    def __str__(self) -> str:
        """Context name for current data.

        We use this context name to keep a reference to data.
        """
        return "__collectable__"

    @abstractmethod
    def __iter__(self) -> Iterator[Collection]:
        """Collect metadata from any kind of data input"""
        ...
