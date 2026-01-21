from sequrity_api.client import SequrityClient

try:
    from sequrity_api._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

__all__ = ["SequrityClient", "__version__"]
