from urllib.parse import quote

from .exceptions import AuthenticationError


def _debug_print(message: str, verbose: bool = False) -> None:
    if verbose:
        print(message)


class AuthMixin:

    def _build_login_payload(self, password: str, is_chita: bool, force_login: bool = False) -> str:
        values = {
            "username": self.username,
            "password": password,
            "forcelogin": "1" if force_login else "0" if is_chita else "1",
        }

        escaped_pairs = []
        for key, value in values.items():
            encoded = quote(str(value), safe="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789*+-._/")
            escaped_pairs.append(f'"{key}":"{encoded}"')

        return "{" + ", ".join(escaped_pairs) + "}"

    def login(self, verbose: bool = False):

        info = self.router_info()
        _debug_print(f"Router model: {info.model}", verbose)

        password = self.password
        is_chita = info.model.upper().startswith("CHITA")

        if is_chita:
            from .crypto import SJCL

            password = SJCL.encrypt(
                self.username,
                self.password,
            )
            _debug_print("Used CHITA password encryption", verbose)
        else:
            _debug_print("CHITA encryption not used for this router", verbose)

        for force_login in (False, True):
            payload = self._build_login_payload(password, is_chita, force_login=force_login)
            _debug_print(f"Login payload: {payload}", verbose)

            r = self.session.post(
                self.url("/1/Device/Users/Login"),
                data={"model": payload},
            )

            _debug_print(f"Login response status: {r.status_code}", verbose)
            _debug_print(f"Login response body: {r.text}", verbose)

            try:
                reply = r.json()
            except ValueError:
                reply = {}

            if reply.get("result") == "success":
                self.get_csrf()
                return True

            if reply.get("result") == "repeatlogin" and not force_login:
                _debug_print("Router reported repeatlogin; attempting logout and retry with force-login", verbose)
                try:
                    self.logout()
                except Exception:
                    pass
                continue

            break

        raise AuthenticationError(reply.get("result", "login failed"))

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
