import json

from .exceptions import AuthenticationError


class AuthMixin:

    def login(self):

        info = self.router_info()

        password = self.password

        if info.model.upper().startswith("CHITA"):

            from .crypto import SJCL

            password = SJCL.encrypt(
                self.username,
                self.password,
            )

        model = {
            "username": self.username,
            "password": password,
        }

        if info.model.upper().startswith("CHITA"):
            model["forcelogin"] = "0"

        r = self.session.post(
            self.url("/1/Device/Users/Login"),
            data={
                "model": json.dumps(model)
            },
        )

        reply = r.json()

        if reply["result"] != "success":
            raise AuthenticationError(reply["result"])

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
