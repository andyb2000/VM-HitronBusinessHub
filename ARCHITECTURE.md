# VMHub Architecture

## Overview

This document describes the architecture of the Virgin Media Hub 5 (Hitron CHITA) web interface and summarises what has been learned by reverse engineering the firmware.

The aim of the VMHub project is **not** to emulate browser behaviour, but to implement a native Python client that speaks the router's internal HTTP API directly.

This document should be treated as the reference for future development.

---

# Router Architecture

The Hub 5 web interface is a JavaScript Single Page Application (SPA).

The browser downloads HTML and JavaScript files which communicate with an internal REST-style API hosted by the router itself.

Typical URL layout:

```
http://192.168.0.1/

index.html
login.html
css/
img/
lib/
```

Most router functionality is implemented through HTTP endpoints under:

```
/1/Device/
```

Examples:

```
/1/Device/Users/Login
/1/Device/Users/Logout
/1/Device/Users/CSRF
/1/Device/Users/Name

/1/Device/CM/Basicinfo
```

---

# Authentication Flow

The login process is more involved than a simple username/password POST.

The browser performs the following sequence.

```
Client
   │
   │ GET /1/Device/CM/Basicinfo
   ▼
Router
   │
   │ returns model information
   ▼

Determine router type

↓

If CHITA:

    Encrypt password using SJCL

Else:

    Send plaintext password

↓

POST /1/Device/Users/Login

↓

Receive PHP session cookie

↓

GET /1/Device/Users/CSRF

↓

Store CSRF token

↓

Authenticated session
```

---

# Basicinfo

The first request made by the login page is:

```
GET

/1/Device/CM/Basicinfo
```

This endpoint returns information including:

* modelName
* GUI style
* platform type

The JavaScript uses this information to determine whether the router is a CHITA platform.

Pseudo-code:

```
if ($.hitron.isChita()) {

    encrypt password

} else {

    send plaintext

}
```

---

# Password Encryption

The router uses the Stanford Javascript Crypto Library (SJCL).

The firmware contains:

```
sjcl.js
encrypt-decrypt.js
```

Encryption code:

```javascript
sjcl.encrypt(username, password, {
    adata: randomize(1,0),
    iv: randomize(4,0),
    salt: randomize(2,0),
    iter:10000,
    mode:"gcm",
    ts:64,
    ks:128
});
```

Important observations:

| Setting             | Value           |
| ------------------- | --------------- |
| Cipher              | AES             |
| Mode                | GCM             |
| Key Size            | 128 bit         |
| Authentication Tag  | 64 bit          |
| PBKDF2 Iterations   | 10000           |
| Encryption Password | Username        |
| Plaintext           | Router password |

The username is used as the encryption password.

The router password becomes the plaintext.

Random values are generated for:

* IV
* Salt
* Additional authenticated data (adata)

The output is JSON.

Example structure:

```json
{
  "iv": "...",
  "v": 1,
  "iter": 10000,
  "ks": 128,
  "ts": 64,
  "mode": "gcm",
  "adata": "...",
  "cipher": "aes",
  "salt": "...",
  "ct": "..."
}
```

The browser URL-escapes this JSON before transmitting it.

---

# Login Request

The browser sends:

```
POST

/1/Device/Users/Login
```

Form data:

```
model=<JSON STRING>
```

Example:

```json
{
    "username":"admin",
    "password":"<encrypted SJCL JSON>",
    "forcelogin":"0"
}
```

If the router is not CHITA:

```
password = plaintext
```

instead.

---

# Force Login

The firmware supports forced session takeover.

Normal login:

```
forcelogin = "0"
```

If another session exists the router returns:

```
repeatlogin
```

The UI prompts the user.

If accepted:

```
forcelogin = "1"
```

The login is attempted again.

VMHub should expose this as:

```python
hub.login(force=True)
```

---

# Session Management

Successful login creates a PHP session.

Observed cookie:

```
PHPSESSID=...
```

Additional cookies include:

```
LANG_COOKIE
modelname
isEdit
...
```

Most appear to be UI-only.

The essential authentication cookie is:

```
PHPSESSID
```

---

# CSRF Protection

After login the browser immediately requests:

```
GET

/1/Device/Users/CSRF
```

Example JavaScript:

```javascript
$.getJSON("/1/Device/Users/CSRF", function(json){

    $("#csrf_token").val(json.CSRF);

});
```

The returned token is stored in a hidden form field.

---

# POST Requests

The firmware overrides Backbone.sync().

Every POST request automatically includes the CSRF token.

Observed code:

```javascript
params.data = params.data ?
{
    model: params.data,
    csrf: $("#csrf_token").val()
}
:
{};
```

Therefore all POST requests become:

```
model=<json>

csrf=<token>
```

This should happen automatically inside the transport layer.

Client code should never manage CSRF manually.

---

# HTTP Headers

Observed request headers:

```
Accept:
text/html, */*; q=0.01

X-Requested-With:
XMLHttpRequest

Referer:
http://192.168.0.1/webpages/index.html

Cookie:
PHPSESSID=...
```

Nothing unusual was observed.

The router appears tolerant of standard Requests headers.

---

# JavaScript Components

The firmware contains several important JavaScript files.

## login.html

Responsible for:

* login page
* loading Basicinfo
* deciding whether encryption is required
* submitting credentials

---

## encrypt-decrypt.js

Wrapper around SJCL.

Contains:

```
doEncrypt()

doDecrypt()
```

No proprietary cryptography is implemented.

The file simply configures SJCL.

---

## sjcl.js

Stanford Javascript Crypto Library.

This is the canonical implementation used by the router.

Rather than attempting to perfectly reimplement SJCL encoding in Python, VMHub executes the original SJCL code via QuickJS.

Advantages:

* Byte-for-byte compatibility
* Future-proof against encoding differences
* Minimal Python code

---

## hitronSync.js

Overrides Backbone.sync().

Automatically injects:

* CSRF token
* request formatting

This is where POST behaviour was determined.

---

## mainApp.js

Responsible for:

* retrieving CSRF
* retrieving username
* application startup
* UI initialisation

---

# Proposed Python Architecture

```
VMHub
 │
 ├── Client
 │
 ├── Session
 │      │
 │      ├── Login
 │      ├── Logout
 │      └── CSRF
 │
 ├── Transport
 │      │
 │      ├── GET
 │      ├── POST
 │      ├── Cookies
 │      └── Retries
 │
 ├── Crypto
 │      │
 │      └── SJCL via QuickJS
 │
 └── API
        │
        ├── Status
        ├── WiFi
        ├── DHCP
        ├── Firewall
        └── Administration
```

The public API should remain small:

```python
hub.login()

hub.status()

hub.devices()

hub.reboot()
```

Everything else should remain internal.

---

# Guiding Principles

* Do not emulate browser behaviour.
* Do not require Selenium or Playwright.
* Encapsulate all HTTP behaviour behind the transport layer.
* Hide CSRF management from library users.
* Hide cookie management from library users.
* Hide encryption from library users.
* Prefer clean Python abstractions over exposing raw endpoints.
* Keep the public API stable even if router firmware changes internally.

---

# Outstanding Unknowns

The following areas remain to be investigated.

* Complete API endpoint enumeration
* Firmware differences between Hub variants
* Session timeout behaviour
* File upload/download endpoints
* Firmware update API
* Event log API
* DOCSIS diagnostics
* Backup/restore configuration
* WebSocket or long-polling endpoints (if any)

These should be documented here as they are discovered.

---

# Development Strategy

Development should proceed in small milestones.

## Phase 1

* HTTP transport
* SJCL wrapper
* Login
* Session management
* CSRF

## Phase 2

* Generic GET/POST wrapper
* Endpoint abstraction
* Status APIs

## Phase 3

* Wi-Fi management
* DHCP
* Connected devices
* Firewall

## Phase 4

* Complete API coverage
* Unit tests
* Documentation
* PyPI packaging

This document should evolve alongside the project and remain the authoritative description of how the router's web interface operates.
