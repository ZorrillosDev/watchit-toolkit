from __future__ import annotations

import asyncio

from dataclasses import dataclass
from nucleus.core.types import Any

SubProcess = asyncio.subprocess.Process
Reader = asyncio.StreamReader
Loop = asyncio.BaseEventLoop


@dataclass
class StdOut:
    exit_code: int
    output: Any

    # TODO use as bytes
    # TODO add methods for handle output
    # TODO eg. as_str, etc
