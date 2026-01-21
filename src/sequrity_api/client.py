import httpx

from .constants import SEQURITY_API_URL
from .control.wrapper import ControlAPIWrapper


class SequrityClient:
    def __init__(self, api_key: str, base_url: str | None = None, timeout: int = 30):
        self._api_key = api_key
        self._base_url = base_url or SEQURITY_API_URL
        self._client = httpx.Client(timeout=timeout)
        self.control = ControlAPIWrapper(client=self._client, base_url=self._base_url, api_key=self._api_key)
