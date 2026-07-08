import base64
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from vmhub.crypto import SJCL


def test_sjcl_encrypt_emits_gcm_payload() -> None:
    payload = SJCL.encrypt("admin", "password")

    data = json.loads(payload)
    assert data["mode"] == "gcm"
    assert data["iter"] == 10000
    assert data["cipher"] == "aes"
    assert data["ks"] == 128
    assert data["ts"] == 64


def test_sjcl_encrypt_round_trips_with_64_bit_tag() -> None:
    payload = SJCL.encrypt("admin", "39000675")
    data = json.loads(payload)

    salt = base64.b64decode(data["salt"])
    iv = base64.b64decode(data["iv"])
    adata = base64.b64decode(data["adata"])
    ct_bytes = base64.b64decode(data["ct"])

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,
        salt=salt,
        iterations=10000,
    )
    key = kdf.derive(b"admin")

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, ct_bytes[-8:], min_tag_length=8),
    ).decryptor()
    decryptor.authenticate_additional_data(adata)
    plaintext = decryptor.update(ct_bytes[:-8]) + decryptor.finalize()

    assert plaintext == b"39000675"
