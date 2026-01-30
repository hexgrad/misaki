"""
uv run --extra vi examples/vi.py
"""

from misaki import vi

g2p = vi.VIG2P()
text = "Misaki là một bộ máy G2P."

phonemes, _ = g2p(text)
print(phonemes)
