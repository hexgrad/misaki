import re
import json
from pathlib import Path

_percent_re = re.compile(r"([ ]?[%])")
_url_re = re.compile(r"([a-zA-Z])\.(com|gov|org|vn|com.vn|edu.vn)")


_abbreviations_vi = {
    "v\.v": " vân vân. ",
    "v/v": "về việc",
    "đ/c": "địa chỉ",
    "k/g": "kính gửi",
    "th/g": "thân gửi",
    "ko": "không",
    "bit": "biết",
    "bik": "biết",
}
_abbreviations_vi.update(
    json.loads(Path(__file__, '..', '..', 'data', 'vi_teencode.json').resolve().read_text(encoding="utf-8"))
)

_abbreviations_combine_re = r"(" + "|".join(_abbreviations_vi.keys()) + r")"

def _expand_percent_vi(m):
    return " phần trăm"


def _expand_urls_vi(m):
    return f"{m.group(1)} chấm {m.group(2)}"


def _expand_abbreviations_vi(m):
    key = m.group(0)
    key = key.replace(".", "\.").lower()
    return _abbreviations_vi[key]


def normalize_abbreviations_vi(text):
    text = normalize_speacial_symbol_vi(text)
    text = re.sub(_url_re, _expand_urls_vi, text)
    text = re.sub(r"\b" + _abbreviations_combine_re + r"\b", _expand_abbreviations_vi, text, flags=re.IGNORECASE)
    return text


def normalize_speacial_symbol_vi(text):
    text = re.sub(_percent_re, _expand_percent_vi, text)
    text = re.sub("&", " và ", text)
    text = re.sub("@", " a còng ", text)
    text = re.sub("\+", " cộng ", text)
    text = re.sub("//", " xuyệt ", text)
    return text
