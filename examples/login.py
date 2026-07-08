from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests

from vmhub import VMHub
from vmhub.crypto import SJCL
from vmhub.exceptions import AuthenticationError


def main() -> int:
    parser = argparse.ArgumentParser(description="Connect to a Virgin Media hub and authenticate")
    parser.add_argument("--host", default=os.getenv("VMHUB_HOST", "192.168.0.1"), help="Router address")
    parser.add_argument("--username", default=os.getenv("VMHUB_USERNAME", "admin"), help="Router username")
    parser.add_argument("--password", default=os.getenv("VMHUB_PASSWORD", ""), help="Router password")
    parser.add_argument("--https", action="store_true", help="Use HTTPS instead of HTTP")
    parser.add_argument("--verbose", action="store_true", help="Print the detailed login request and response information")
    args = parser.parse_args()

    if not args.password:
        parser.error("a password is required, either via --password or the VMHUB_PASSWORD environment variable")

    with VMHub(host=args.host, username=args.username, password=args.password, https=args.https, verbose=args.verbose) as client:
        try:
            client.login(verbose=args.verbose)
        except requests.exceptions.RequestException as exc:
            print(f"Connection failed: {exc}")
            return 1
        except AuthenticationError as exc:
            print(f"Authentication failed: {exc}")
            return 1

        print("Login successful.")
        print(f"Authenticated: {client.is_authenticated()}")
        print(f"CSRF token: {client.session.csrf}")
        if getattr(SJCL, "_context", None) is None:
            print("Note: the CHITA encryption path is unavailable; the login used the fallback behavior.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
