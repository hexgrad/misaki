"""
uv run --extra ko examples/ko.py
"""

from misaki import ko

g2p = ko.KOG2P()
text = "미사키는 G2P 엔진입니다."

phonemes, _ = g2p(text)
print(phonemes)
