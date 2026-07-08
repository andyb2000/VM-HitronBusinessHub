from dataclasses import dataclass


@dataclass
class RouterInfo:
    model: str
    gui_style: str | None = None
