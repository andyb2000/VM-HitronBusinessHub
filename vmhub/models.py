from dataclasses import dataclass
from typing import Optional


@dataclass
class RouterInfo:
    model: str
    gui_style: Optional[str] = None
