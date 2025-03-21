import re

from .symbol_vi import vietnamese_without_num_re
from pathlib import Path
import json

_currency_key = {
    "\$": "đô la",
    "£": "bảng",
    "€": "ơ rô",
    "₩": "uân",
    "₫": "đồng",
    "usd": "đô la",
    "euro": "ơ rô",
    "eur": "ơ rô",
    "vnd": "đồng",
    "đ": "đồng",
    "¥": "yên",
    "ndt": "nhân dân tệ",
    "%": "phần trăm"
}
_currency_key.update(json.loads(
    Path(__file__, '..', '..', 'data', 'vi_symbols.json').resolve().read_text(encoding="utf-8")
))


_currency_combine_regex = "|".join(re.escape(key) for key in _currency_key.keys())
_currency_vi_re = re.compile(vietnamese_without_num_re + r"(" + _currency_combine_regex + ")" + vietnamese_without_num_re, re.IGNORECASE)


def _expand_currency(match):
    prefix, currency, suffix = match.groups(0)
    prefix = "" if prefix == 0 else prefix
    suffix = "" if suffix == 0 else suffix
    if currency == "Đ" and suffix == ".":
        return match.group(0)
    if suffix == currency or prefix == currency:
        return match.group(0)
    if currency.lower() == "$":
        currency = _currency_key["\$"]
    elif currency.lower() in _currency_key.keys():
        currency = _currency_key[currency.lower()]
    return prefix + currency + suffix


def normalize_currency_vi(text):
    text = re.sub(_currency_vi_re, _expand_currency, text)
    return text
