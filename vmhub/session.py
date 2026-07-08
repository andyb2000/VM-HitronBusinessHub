import requests


class VMHubSession(requests.Session):

    def __init__(self):

        super().__init__()

        self.headers.update(
            {
                "User-Agent": "VMHub Python Library",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "",
            }
        )

        self.csrf = None
