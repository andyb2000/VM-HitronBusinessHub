# Reverse Engineering Notes

This document is an informal engineering notebook used during development.

Unlike `ARCHITECTURE.md`, this file contains observations, experiments, hypotheses, and future investigation ideas. Information here may be incomplete or later proven incorrect.

---

# Firmware

Current target:

* Virgin Media Hub 5
* Hitron CHITA platform

The web interface is a JavaScript single-page application.

Relevant firmware files:

```
login.html
index.html

lib/
    sjcl.js
    encrypt-decrypt.js
    hitronSync.js
    jquery.hitronext.js
    backbone.js
    mainApp.js
```

---

# Authentication

## Login flow

Observed browser sequence:

```
GET /1/Device/CM/Basicinfo

↓

Determine platform

↓

If CHITA

↓

Encrypt password

↓

POST /1/Device/Users/Login

↓

Receive PHPSESSID

↓

GET /1/Device/Users/CSRF

↓

Authenticated
```

This flow has been verified from the firmware JavaScript.

---

## Basicinfo

Endpoint:

```
GET /1/Device/CM/Basicinfo
```

Returns:

* modelName
* GuiStyle
* platform information

Used by login.html before authentication.

Need to investigate whether additional fields are useful.

---

## Password Encryption

The firmware includes:

```
encrypt-decrypt.js
sjcl.js
```

Encryption function:

```
doEncrypt(username, password)
```

Internally this simply calls:

```
sjcl.encrypt(...)
```

No proprietary algorithm appears to be implemented.

Parameters observed:

```
AES-GCM

PBKDF2

10000 iterations

128-bit key

64-bit authentication tag

username used as encryption password
```

Current plan:

Execute SJCL directly using QuickJS rather than rewriting the algorithm in Python.

---

## Login POST

Observed payload:

```
model=<JSON>
```

JSON:

```json
{
    "username":"admin",
    "password":"<encrypted JSON>",
    "forcelogin":"0"
}
```

Need to confirm whether additional fields ever appear.

---

## Force Login

Firmware supports:

```
forcelogin=0

forcelogin=1
```

If another administrator is logged in:

```
repeatlogin
```

is returned.

The browser offers to terminate the existing session.

Python API should expose:

```
login(force=True)
```

---

# Session

Observed cookie:

```
PHPSESSID
```

Other cookies:

```
LANG_COOKIE

modelname

isEdit

isEdit1

isEdit2

isEdit3
```

Current assumption:

Only PHPSESSID is required.

Need to verify by stripping optional cookies.

---

# CSRF

Observed endpoint:

```
GET /1/Device/Users/CSRF
```

Returns JSON:

```json
{
    "CSRF":"..."
}
```

Stored in a hidden HTML field.

Need to determine:

* expiry
* regeneration rules
* whether it changes after login
* whether it changes after reboot

---

# Backbone.sync()

The firmware overrides Backbone.sync().

Observed behaviour:

```
POST data becomes

model=<json>

csrf=<token>
```

Need to determine whether PUT/DELETE requests also include CSRF.

---

# HTTP Headers

Observed browser headers:

```
X-Requested-With: XMLHttpRequest

Referer: index.html

Accept: text/html, */*
```

Need to determine whether any headers are mandatory.

---

# JavaScript Files

## login.html

Responsibilities:

* login form
* platform detection
* authentication

Status:

✓ Understood

---

## encrypt-decrypt.js

Responsibilities:

* wrapper around SJCL

Status:

✓ Fully understood

---

## sjcl.js

Responsibilities:

* encryption

Status:

Not analysed internally.

Treat as trusted third-party library.

---

## hitronSync.js

Responsibilities:

* overrides Backbone.sync()
* injects CSRF

Status:

Mostly understood.

Need to inspect remaining methods.

---

## mainApp.js

Responsibilities:

* startup
* fetch username
* fetch CSRF
* initialise SPA

Status:

Partially analysed.

---

# Endpoint Discovery

Known endpoints:

```
/1/Device/CM/Basicinfo

/1/Device/Users/Login

/1/Device/Users/Logout

/1/Device/Users/CSRF

/1/Device/Users/Name
```

Need to continue extracting endpoints from JavaScript.

Potential approach:

```
grep "/1/Device/"
```

or

```
grep ".fetch("
```

or

```
grep "$.get"

grep "$.post"

grep "$.ajax"
```

---

# Questions

Open questions:

* Session timeout?
* Maximum simultaneous sessions?
* API versioning?
* Firmware differences?
* Backup API?
* DOCSIS diagnostics?
* Event log?
* Reboot endpoint?
* Factory reset endpoint?
* Upload/download APIs?
* Firmware update API?
* WebSocket support?
* Long polling?

---

# Future Investigation

When analysing new firmware:

* Compare login.html
* Compare encrypt-decrypt.js
* Compare hitronSync.js
* Compare mainApp.js
* Enumerate new endpoints
* Compare API responses
* Check authentication changes
* Check CSRF behaviour

---

# Coding Principles

The Python library should:

* never expose raw HTTP unnecessarily
* automatically manage sessions
* automatically manage cookies
* automatically manage CSRF
* automatically encrypt passwords
* provide a simple, Pythonic API

Goal:

```python
from vmhub import VMHub

hub = VMHub(
    host="192.168.0.1",
    username="admin",
    password="password"
)

hub.login()

print(hub.status())

print(hub.devices())

hub.reboot()
```

No user of the library should ever need to know how the browser implements authentication.
