from .g2pkc import G2p

class KOG2P:
    def __init__(self):
        self.g2pk = G2p()

    def __call__(self, text):
        ps = self.g2pk(text)
        return ps
