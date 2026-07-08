from pathlib import Path

from quickjs import Context


class SJCL:
    """Thin wrapper around the firmware's embedded SJCL implementation."""

    _context: Context | None = None

    @classmethod
    def _load_context(cls) -> Context:
        if cls._context is None:
            firmware_root = Path(__file__).resolve().parents[1] / "firmware" / "lib"
            ctx = Context()
            ctx.eval((firmware_root / "sjcl.js").read_text())
            ctx.eval((firmware_root / "encrypt-decrypt.js").read_text())
            cls._context = ctx

        return cls._context

    @classmethod
    def encrypt(cls, key: str, plaintext: str) -> str:
        if not key or not plaintext:
            raise ValueError("key and plaintext are required")

        ctx = cls._load_context()
        ctx.set("vmhub_key", key)
        ctx.set("vmhub_plaintext", plaintext)

        encrypted = ctx.eval("doEncrypt(vmhub_key, vmhub_plaintext)")
        return str(encrypted)
