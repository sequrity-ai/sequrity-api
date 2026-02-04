"""Sequrity API Python client.

This package provides a Python client for interacting with the Sequrity API,
enabling secure LLM interactions with policy enforcement.
"""

from sequrity.client import SequrityClient

try:
    from sequrity._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

__all__ = ["SequrityClient", "__version__"]
