"""Generic SSE stream wrappers for typed chunk iteration."""

from __future__ import annotations

import json
from typing import AsyncIterator, Generic, Iterator, TypeVar

import httpx
from pydantic import TypeAdapter

_T = TypeVar("_T")


class SyncStream(Generic[_T]):
    """Wraps an httpx streaming response, parses SSE lines, and yields typed chunks.

    Usage::

        stream = SyncStream(response, ChatCompletionChunk)
        for chunk in stream:
            print(chunk)
        stream.close()

    Or as a context manager::

        with SyncStream(response, ChatCompletionChunk) as stream:
            for chunk in stream:
                print(chunk)
    """

    def __init__(
        self,
        response: httpx.Response,
        chunk_type: type[_T],
        *,
        session_id: str | None = None,
    ) -> None:
        self._response = response
        self._adapter = TypeAdapter(chunk_type)
        self.session_id = session_id

    def __iter__(self) -> Iterator[_T]:
        for line in self._response.iter_lines():
            chunk = _parse_sse_line(line, self._adapter)
            if chunk is not None:
                yield chunk

    def __enter__(self) -> SyncStream[_T]:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP response."""
        self._response.close()


class AsyncStream(Generic[_T]):
    """Async variant of :class:`SyncStream`.

    Usage::

        async with AsyncStream(response, ChatCompletionChunk) as stream:
            async for chunk in stream:
                print(chunk)
    """

    def __init__(
        self,
        response: httpx.Response,
        chunk_type: type[_T],
        *,
        session_id: str | None = None,
    ) -> None:
        self._response = response
        self._adapter = TypeAdapter(chunk_type)
        self.session_id = session_id

    async def __aiter__(self) -> AsyncIterator[_T]:
        async for line in self._response.aiter_lines():
            chunk = _parse_sse_line(line, self._adapter)
            if chunk is not None:
                yield chunk

    async def __aenter__(self) -> AsyncStream[_T]:
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP response."""
        await self._response.aclose()


def _parse_sse_line(line: str, adapter: TypeAdapter[_T]) -> _T | None:
    """Parse a single SSE line and return a validated chunk, or None if the line should be skipped."""
    # Skip empty lines, comment lines, and event type lines
    if not line or line.startswith(":") or line.startswith("event:"):
        return None

    # Strip "data: " prefix
    if line.startswith("data: "):
        line = line[6:]
    elif line.startswith("data:"):
        line = line[5:]
    else:
        return None

    # Skip the [DONE] sentinel
    if line.strip() == "[DONE]":
        return None

    return adapter.validate_python(json.loads(line))
