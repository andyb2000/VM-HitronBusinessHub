import json

from vmhub.crypto import SJCL


def test_sjcl_encrypt_emits_gcm_payload() -> None:
    payload = SJCL.encrypt("admin", "password")

    data = json.loads(payload)
    assert data["mode"] == "gcm"
    assert data["iter"] == 10000
    assert data["cipher"] == "aes"
    assert data["ks"] == 128
    assert data["ts"] == 64
