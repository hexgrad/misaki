from .g2pkc import G2p
from typing import Tuple

class KOG2P:
    def __init__(self):
        self.g2pk = G2p()

    def __call__(self, text) -> Tuple[str, None]:
        # TODO: Return List[MToken] instead of None
        ps = self.g2pk(text)
        return ps, None
