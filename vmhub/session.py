import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class VMHubSession(requests.Session):

    def __init__(self, timeout: int = 20):

        super().__init__()

        self.timeout = timeout
        self.headers.update(
            {
                "User-Agent": "VMHub Python Library",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "",
            }
        )

        retry_policy = Retry(total=0, connect=0, read=0, redirect=0, status=0)
        adapter = HTTPAdapter(max_retries=retry_policy)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

        self.csrf = None

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return super().request(method, url, **kwargs)

    def close(self):
        self.csrf = None
        super().close()
