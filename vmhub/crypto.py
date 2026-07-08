import base64
import json
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SJCL:
    """Thin wrapper around the firmware's embedded SJCL implementation."""

    @staticmethod
    def encrypt(key: str, plaintext: str) -> str:
        if not key or not plaintext:
            raise ValueError("key and plaintext are required")

        salt = os.urandom(8)
        iv = os.urandom(16)
        adata = os.urandom(4)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,
            salt=salt,
            iterations=10000,
        )
        derived_key = kdf.derive(key.encode("utf-8"))

        encryptor = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv, min_tag_length=8),
        ).encryptor()
        encryptor.authenticate_additional_data(adata)
        ciphertext = encryptor.update(plaintext.encode("utf-8")) + encryptor.finalize()
        ciphertext += encryptor.tag[:8]

        payload = {
            "v": 1,
            "iter": 10000,
            "ks": 128,
            "ts": 64,
            "mode": "gcm",
            "adata": base64.b64encode(adata).decode("ascii"),
            "cipher": "aes",
            "salt": base64.b64encode(salt).decode("ascii"),
            "iv": base64.b64encode(iv).decode("ascii"),
            "ct": base64.b64encode(ciphertext).decode("ascii"),
        }
        return json.dumps(payload, separators=(",", ":"))
