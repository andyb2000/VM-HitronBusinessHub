import requests
import requests.sessions

from vmhub import VMHub


def test_vmhub_can_be_instantiated() -> None:
    hub = VMHub(host="192.168.0.1", username="admin", password="password")

    assert hub.base == "http://192.168.0.1"
    assert hub.username == "admin"
    assert hub.password == "password"


def test_session_uses_single_attempt_and_default_timeout(monkeypatch) -> None:
    hub = VMHub(host="192.168.0.1", username="admin", password="password")

    assert hub.session.timeout == 20
    assert hub.session.adapters["https://"].max_retries.total == 0

    captured = {}

    def fake_request(self, method, url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            response = requests.Response()
            response.status_code = 200
            response._content = b"{}"
            response.url = url
            return response
    monkeypatch.setattr(requests.sessions.Session, "request", fake_request)

    hub.session.get("https://example.com")

    assert captured["timeout"] == 20
