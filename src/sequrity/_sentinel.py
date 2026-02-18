"""NOT_GIVEN sentinel for distinguishing 'not passed' from 'passed None'.

When a user calls ``client.chat.create(features=None)``, that means "explicitly
no features header". When they omit ``features`` entirely, the client should
fall back to the default set at client init time. The ``NOT_GIVEN`` sentinel
makes this distinction possible.
"""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


class _NotGiven:
    """Sentinel class for parameters that were not provided."""

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = _NotGiven()
"""Singleton sentinel value indicating a parameter was not provided."""
