"""
uv run --extra ja examples/ja.py
"""

from misaki import ja

g2p = ja.JAG2P(version="pyopenjtalk")
text = "みさきはG2Pエンジンです。"

phonemes, _ = g2p(text)
print(phonemes)
