# VMHub

A Python library for interacting with Virgin Media Hub 5 (Hitron CHITA) routers via their undocumented HTTP API.

## Overview

VMHub is a clean, Pythonic interface to the management API exposed by Virgin Media Hub 5 routers based on the Hitron CHITA platform.

The router's web interface is implemented almost entirely in JavaScript, communicating with an internal REST-style API. This project reverse-engineers that API and provides a modern Python library for interacting with it programmatically.

The long-term aim is to support both monitoring and administration of the router without requiring browser automation.

---

## Setup on a fresh server

Clone the repository and create a virtual environment:

```bash
git clone <repo-url>
cd VM-HitronBusinessHub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you prefer the modern packaging flow, you can also install the project in editable mode:

```bash
pip install -e .
```

To run the sample login example:

```bash
python examples/login.py --host 192.168.0.1 --username admin --password 'your-password'
```

You can also provide the credentials through environment variables:

```bash
export VMHUB_HOST=192.168.0.1
export VMHUB_USERNAME=admin
export VMHUB_PASSWORD='your-password'
python examples/login.py
```

---

## Project Goals

* Native Python implementation
* No browser automation or Selenium
* Full session and login handling
* Compatible with encrypted CHITA authentication
* Modular architecture
* Well documented
* Fully typed where practical
* Suitable for automation and Home Assistant integrations

---

## Current Status

The project is currently in active development.

The initial milestone is implementing reliable authentication against the router using the same encryption mechanism as the official web interface.

Known implementation details include:

* Authentication uses the router's `/1/Device/Users/Login` endpoint.
* CHITA firmware encrypts passwords using the Stanford Javascript Crypto Library (SJCL).
* Passwords are encrypted with AES-GCM.
* The encryption key is the username.
* PBKDF2 with 10,000 iterations is used for key derivation.
* Authentication returns a PHP session cookie.
* A CSRF token must subsequently be obtained from `/1/Device/Users/CSRF`.
* Future API requests include the CSRF token alongside request payloads.

---

## Planned Features

### Authentication

* Login
* Logout
* Automatic session handling
* Automatic CSRF management
* Force-login support
* Session renewal

### Status

* System information
* WAN status
* DOCSIS status
* Firmware information
* Uptime
* Event log

### Network

* Connected devices
* DHCP leases
* Reserved addresses
* Port forwarding
* UPnP
* Firewall configuration
* IPv4/IPv6 information

### Wireless

* 2.4 GHz configuration
* 5 GHz configuration
* Guest Wi-Fi
* Channel information
* Signal settings
* Radio control

### Administration

* Reboot
* Backup configuration
* Restore configuration
* Factory reset
* User management

---

## Proposed Project Structure

```
VM-HistronBusinessHub/
│
├── README.md                <- What the project is
├── ARCHITECTURE.md          <- How the firmware/API works
├── ENDPOINTS.md             <- Every discovered REST endpoint
├── NOTES.md                 <- Investigation notes & TODOs
├── LICENSE
├── pyproject.toml
│
├── vmhub/
│   ├── __init__.py
│   ├── client.py
│   ├── session.py
│   ├── crypto.py
│   ├── exceptions.py
│   │
│   ├── api/
│   │   ├── users.py
│   │   ├── device.py
│   │   ├── network.py
│   │   ├── firewall.py
│   │   ├── wifi.py
│   │   ├── advanced.py
│   │   └── ...
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── device.py
│   │   └── ...
│   │
│   └── util/
│       ├── cookies.py
│       ├── csrf.py
│       └── logging.py
│
├── firmware/
│
├── tests/
│
├── docs/
│   ├── login.md
│   ├── crypto.md
│   ├── packet-captures.md
│   ├── reverse-engineering.md
│   └── firmware-notes.md
│
└── examples/
    ├── login.py
    ├── reboot.py
    ├── wifi.py
    └── port_forward.py

```

---

## Authentication

Unlike previous Virgin Media hubs, the Hub 5 does not simply POST the username and password.

The browser performs the following sequence:

1. Query `/1/Device/CM/Basicinfo`
2. Determine whether the router is a CHITA platform
3. Encrypt the password using SJCL (AES-GCM)
4. POST credentials to `/1/Device/Users/Login`
5. Receive PHP session cookie
6. Request `/1/Device/Users/CSRF`
7. Include the CSRF token in subsequent POST requests

VMHub mirrors this process rather than attempting to emulate browser behaviour.

---

## Design Principles

The public API should be simple.

Example:

```python
from vmhub import VMHub

hub = VMHub(
    host="192.168.0.1",
    username="admin",
    password="password"
)

hub.login()

status = hub.status()
devices = hub.devices()
wifi = hub.wifi()

hub.reboot()
```

Users should never need to manually manage:

* cookies
* sessions
* CSRF tokens
* password encryption
* HTTP headers
* retries

These responsibilities belong inside the library.

---

## Reverse Engineering

This project has been developed by analysing the JavaScript delivered by the router's management interface.

The repository may contain original firmware JavaScript files under the `firmware/` directory purely for reference during development.

These files are **not** modified or redistributed as part of the Python library itself.

---

## Development Roadmap

### Phase 1

* HTTP transport layer
* SJCL encryption wrapper
* Login
* Session management
* CSRF handling

### Phase 2

* Generic REST client
* Endpoint discovery
* Device information
* Status APIs

### Phase 3

* Wi-Fi configuration
* DHCP management
* Firewall
* Port forwarding

### Phase 4

* Complete API coverage
* Unit tests
* Documentation
* Packaging
* Home Assistant integration

---

## Requirements

* Python 3.8+
* requests 2.31.x (newer releases require newer Python versions)
* quickjs

---

## Disclaimer

This project is an independent reverse-engineering effort and is not affiliated with Virgin Media, Liberty Global, Hitron Technologies, or any router manufacturer.

Use at your own risk. Configuration changes performed through undocumented APIs may have unintended effects, and future firmware updates may change or remove functionality.

Further disclaimer - I used codex to assist in this project, so AI generated errors are likely ;-)

