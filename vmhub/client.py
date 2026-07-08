import atexit
import json

from .session import VMHubSession
from .models import RouterInfo
from .auth import AuthMixin


class VMHubClient(AuthMixin):

    def __init__(
        self,
        host,
        username,
        password,
        https=False,
        verbose=False,
    ):

        proto = "https" if https else "http"

        self.base = f"{proto}://{host}"

        self.username = username
        self.password = password
        self.verbose = verbose

        self.session = VMHubSession()
        self._closed = False
        self._should_logout = False
        self.session._logout_on_close = False

        self.session.headers["Referer"] = (
            self.base + "/webpages/index.html"
        )

        atexit.register(self.close)

    def url(self, path):

        return self.base + path

    def router_info(self):

        r = self.session.get(
            self.url("/1/Device/CM/Basicinfo")
        )

        if self.verbose:
            print(f"Basicinfo status: {r.status_code}")
            print(f"Basicinfo body: {r.text}")

        j = r.json()

        return RouterInfo(
            model=j["modelName"],
            gui_style=j.get("GuiStyle"),
        )

    def is_authenticated(self) -> bool:
        return bool(self.session.csrf or self.session.cookies.get("PHPSESSID"))

    def login(self, verbose: bool = None):
        if verbose is None:
            verbose = self.verbose

        result = super().login(verbose=verbose)
        self._should_logout = True
        self.session._logout_on_close = True
        return result

    def close(self, verbose: bool = None):
        if verbose is None:
            verbose = self.verbose

        if getattr(self, "_closed", False):
            return

        self._closed = True

        if self._should_logout or getattr(self.session, "_logout_on_close", False):
            try:
                self.logout(verbose=verbose)
            except Exception:
                pass
            finally:
                self._should_logout = False
                self.session._logout_on_close = False

        try:
            self.session.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def get(self, endpoint):

        r = self.session.get(
            self.url("/1/Device/" + endpoint)
        )

        return r.json()

    def put(self, endpoint, model):

        model["_method"] = "PUT"

        r = self.session.post(
            self.url("/1/Device/" + endpoint),
            data={
                "model": json.dumps(model),
                "csrf": self.session.csrf,
            },
        )

        return r.json()
