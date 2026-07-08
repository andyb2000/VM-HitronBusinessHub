class VMHubError(Exception):
    """Base exception."""


class LoginError(VMHubError):
    pass


class AuthenticationError(VMHubError):
    pass


class RouterError(VMHubError):
    pass


class APIError(VMHubError):
    pass
