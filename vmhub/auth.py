from urllib.parse import quote

from .exceptions import AuthenticationError


class AuthMixin:

    def _build_login_payload(self, password: str, is_chita: bool) -> str:
        values = {
            "username": self.username,
            "password": password,
            "forcelogin": "0" if is_chita else "1",
        }

        escaped_pairs = []
        for key, value in values.items():
            encoded = quote(str(value), safe="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789*+-._/")
            escaped_pairs.append(f'"{key}":"{encoded}"')

        return "{" + ", ".join(escaped_pairs) + "}"

    def login(self):

        info = self.router_info()

        password = self.password
        is_chita = info.model.upper().startswith("CHITA")

        if is_chita:
            from .crypto import SJCL

            password = SJCL.encrypt(
                self.username,
                self.password,
            )

        payload = self._build_login_payload(password, is_chita)

        r = self.session.post(
            self.url("/1/Device/Users/Login"),
            data={"model": payload},
        )

        reply = r.json()

        if reply.get("result") != "success":
            raise AuthenticationError(reply.get("result", "login failed"))

        self.get_csrf()

        return True

    def logout(self):

        self.session.post(
            self.url("/1/Device/Users/Logout")
        )

    def get_csrf(self):

        r = self.session.get(
            self.url("/1/Device/Users/CSRF")
        )

        self.session.csrf = r.json()["CSRF"]

        return self.session.csrf
