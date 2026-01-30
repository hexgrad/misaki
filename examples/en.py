"""
uv run --extra en examples/en.py
"""

from misaki import en

g2p = en.G2P(trf=False, british=False, fallback=None)
text = "Misaki is a G2P engine."

phonemes, _ = g2p(text)
print(phonemes)
