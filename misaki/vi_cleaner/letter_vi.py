import re

from .symbol_vi import vietnamese_set

_letter_key_vi = {
    "a": "ây",
    "b": "bê",
    "c": "xê",
    "d": "dê",
    "đ": "đê",
    "f": "ép",
    "g": "gờ",
    "h": "hát",
    "i": "ai",
    "j": "chây",
    "k": "kây",
    "l": "lờ",
    "m": "em mờ",
    "n": "en nờ",
    "o": "ô",
    "p": "pê",
    "q": "kiu",
    "r": "rờ",
    "s": "ét",
    "t": "ti",
    "v": "vi",
    "w": "vê kép",
    "x": "ít",
    "z": "dét",
}
_letter_combine_re = "|".join(_letter_key_vi.keys())
_quotes_symbol = r"(\"|\')?"
_space = r"(\s)"
_letter_re = r"(chữ|chữ cái|kí tự|ký tự)?" + _space + _quotes_symbol + r"(" + _letter_combine_re + r")" + r"(.)?"


def _expand_letter_vi(match):
    leading, space1, quote1, char, trailing = match.groups(0)
    leading = "" if leading == 0 else leading
    quote1 = "" if quote1 == 0 else quote1
    trailing = "" if trailing == 0 else trailing
    if trailing in vietnamese_set:
        return match.group(0)
    char = char.lower()
    trailing = trailing if trailing != "." else ""
    if char in _letter_key_vi:
        return leading + " " + quote1 + _letter_key_vi[char] + trailing + " "
    return match.group(0)


def normalize_letter_vi(text):
    text = re.sub(_letter_re, _expand_letter_vi, text, flags=re.IGNORECASE)
    return text
