from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class MToken:
    text: str
    tag: str
    whitespace: str
    is_head: bool = True
    alias: Optional[str] = None
    phonemes: Optional[str] = None
    stress: Union[None, int, float] = None
    currency: Optional[str] = None
    num_flags: str = ''
    prespace: bool = False
    rating: Optional[int] = None
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None

    @staticmethod
    def merge_tokens(tokens: List['MToken'], unk: Optional[str] = None) -> 'MToken':
        stress = {t.stress for t in tokens if t.stress is not None}
        currency = {t.currency for t in tokens if t.currency is not None}
        rating = {t.rating for t in tokens}
        if unk is None:
            phonemes = None
        else:
            phonemes = ''
            for t in tokens:
                if t.prespace and phonemes and not phonemes[-1].isspace() and t.phonemes:
                    phonemes += ' '
                phonemes += unk if t.phonemes is None else t.phonemes
        return MToken(
            text=''.join(t.text + t.whitespace for t in tokens[:-1]) + tokens[-1].text,
            tag=max(tokens, key=lambda t: sum(1 if c == c.lower() else 2 for c in t.text)).tag,
            whitespace=tokens[-1].whitespace,
            is_head=tokens[0].is_head,
            alias=None,
            phonemes=phonemes,
            stress=list(stress)[0] if len(stress) == 1 else None,
            currency=max(currency) if currency else None,
            num_flags=''.join(sorted({c for t in tokens for c in t.num_flags})),
            prespace=tokens[0].prespace,
            rating=None if None in rating else min(rating),
            start_ts=tokens[0].start_ts,
            end_ts=tokens[-1].end_ts
        )

    def is_to(self):
        return self.text in ('to', 'To') or (self.text == 'TO' and self.tag in ('TO', 'IN'))

    def debug_all(self):
        ps = {None: '❓', '': '🥷'}.get(self.phonemes, self.phonemes)
        if self.rating is None:
            rt = '❓(UNK)'
        elif self.rating >= 5:
            rt = '💎(5/5)'
        elif self.rating == 4:
            rt = '🏆(4/5)'
        elif self.rating == 3:
            rt = '🥈(3/5)'
        else:
            rt = '🥉(2/5)'
        return [self.text, self.tag, bool(self.whitespace), ps, rt]
