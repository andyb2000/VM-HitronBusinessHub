from pathlib import Path
from typing import Optional

try:
    from quickjs import Context
except Exception:  # pragma: no cover - depends on platform ABI support
    Context = None


class SJCL:
    """Thin wrapper around the firmware's embedded SJCL implementation."""

    _context: Optional[object] = None

    @classmethod
    def _load_context(cls):
        if cls._context is None:
            if Context is None:
                raise RuntimeError(
                    "quickjs is not available in this Python environment; "
                    "the CHITA encryption path cannot be used here"
                )

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

        try:
            ctx = cls._load_context()
        except RuntimeError:
            return plaintext

        ctx.set("vmhub_key", key)
        ctx.set("vmhub_plaintext", plaintext)

        encrypted = ctx.eval("doEncrypt(vmhub_key, vmhub_plaintext)")
        return str(encrypted)
