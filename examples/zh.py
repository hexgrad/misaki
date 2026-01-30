"""
uv run --extra zh examples/zh.py
"""

from misaki import zh

g2p = zh.ZHG2P()
text = "米咲是一个G2P引擎。"

phonemes, _ = g2p(text)
print(phonemes)
