from dataclasses import dataclass
from typing import Optional
import addict

@dataclass
class MToken:
    text: str
    tag: str
    whitespace: str
    phonemes: Optional[str] = None
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None

    class Underscore(addict.Dict):
        def __getattr__(self, key):
            return super().__getattr__(key) if key in self else None

    _: Optional[Underscore] = None
