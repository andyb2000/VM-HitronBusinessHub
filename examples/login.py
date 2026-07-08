from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vmhub import VMHub
from vmhub.exceptions import AuthenticationError


def main() -> int:
    parser = argparse.ArgumentParser(description="Connect to a Virgin Media hub and authenticate")
    parser.add_argument("--host", default=os.getenv("VMHUB_HOST", "192.168.0.1"), help="Router address")
    parser.add_argument("--username", default=os.getenv("VMHUB_USERNAME", "admin"), help="Router username")
    parser.add_argument("--password", default=os.getenv("VMHUB_PASSWORD", ""), help="Router password")
    parser.add_argument("--https", action="store_true", help="Use HTTPS instead of HTTP")
    args = parser.parse_args()

    if not args.password:
        parser.error("a password is required, either via --password or the VMHUB_PASSWORD environment variable")

    client = VMHub(host=args.host, username=args.username, password=args.password, https=args.https)

    try:
        client.login()
    except AuthenticationError as exc:
        print(f"Authentication failed: {exc}")
        return 1

    print("Login successful.")
    print(f"Authenticated: {client.is_authenticated()}")
    print(f"CSRF token: {client.session.csrf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
