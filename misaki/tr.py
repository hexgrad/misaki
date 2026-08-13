"""Turkish G2P: text normalization + espeak-ng phonemization.

normalize_text_tr() expands common Turkish numbers, dates, times, currency,
percentages, units, and abbreviations so espeak-ng receives clean text.

TRG2P wraps normalize_text_tr() + EspeakG2P(language="tr").
"""

from typing import Tuple
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re


_ONES = [
    "",
    "bir",
    "iki",
    "üç",
    "dört",
    "beş",
    "altı",
    "yedi",
    "sekiz",
    "dokuz",
]

_TENS = [
    "",
    "on",
    "yirmi",
    "otuz",
    "kırk",
    "elli",
    "altmış",
    "yetmiş",
    "seksen",
    "doksan",
]

_MONTHS = [
    "",
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
]


def _under_thousand(n: int) -> str:
    if not 0 <= n < 1000:
        raise ValueError("n must be between 0 and 999")

    parts = []

    hundreds, remainder = divmod(n, 100)

    if hundreds:
        if hundreds > 1:
            parts.append(_ONES[hundreds])

        parts.append("yüz")

    tens, ones = divmod(remainder, 10)

    if tens:
        parts.append(_TENS[tens])

    if ones:
        parts.append(_ONES[ones])

    return " ".join(parts)


def _int_to_tr(n: int) -> str:
    """Convert an integer to Turkish words."""

    if n == 0:
        return "sıfır"

    if n < 0:
        return "eksi " + _int_to_tr(-n)

    scales = [
        (1_000_000_000, "milyar"),
        (1_000_000, "milyon"),
        (1_000, "bin"),
    ]

    parts = []
    remainder = n

    for value, word in scales:
        count, remainder = divmod(remainder, value)

        if count:
            if value == 1_000 and count == 1:
                parts.append("bin")
            else:
                parts.append(_int_to_tr(count))
                parts.append(word)

    if remainder:
        parts.append(_under_thousand(remainder))

    return " ".join(parts)


def _decimal_to_tr(value: str) -> str:
    """Convert Turkish decimal notation.

    Example:
        3,14 -> üç virgül bir dört
    """

    integer, fraction = value.split(",", 1)

    return (
        _int_to_tr(int(integer))
        + " virgül "
        + " ".join(_int_to_tr(int(digit)) for digit in fraction)
    )


def _currency_repl(symbol: str, raw: str) -> str:
    names = {
        "₺": ("Türk lirası", "kuruş"),
        "TL": ("Türk lirası", "kuruş"),
        "€": ("euro", "sent"),
        "$": ("dolar", "sent"),
        "£": ("sterlin", "peni"),
    }

    major_name, minor_name = names[symbol]

    cleaned = raw.replace(".", "").replace(",", ".")

    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return f"{raw} {symbol}"

    total_minor = int(
        (value * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    major, minor = divmod(total_minor, 100)

    result = f"{_int_to_tr(major)} {major_name}"

    if minor:
        result += f" {_int_to_tr(minor)} {minor_name}"

    return result


def normalize_text_tr(text: str) -> str:
    """Normalize Turkish text for TTS."""

    if not text:
        return text

    # Typography
    text = (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
    )

    # Non-standard whitespace
    text = re.sub(r"[^\S \n]", " ", text)

    # Common Turkish abbreviations
    replacements = [
        (r"\bDr\.(?=\s)", "Doktor"),
        (r"\bProf\.(?=\s)", "Profesör"),
        (r"\bSn\.(?=\s)", "Sayın"),
        (r"\bAv\.(?=\s)", "Avukat"),
        (r"\bDoç\.(?=\s)", "Doçent"),
        (r"\bT\.C\.", "Türkiye Cumhuriyeti"),
        (r"\bNo\.(?=\s*\d)", "Numara"),
        (r"\börn\.", "örneğin"),
        (r"\bvb\.", "ve benzeri"),
        (r"\bvs\.", "vesaire"),
        (r"\byakl\.", "yaklaşık"),
    ]

    for pattern, replacement in replacements:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE,
        )

    # Technical and engineering units
    #
    # Specific forms should be replaced before general forms.
    unit_replacements = [
        (r"\bkW['’]lık\b", "kilovatlık"),
        (r"\bkWh\b", "kilovat saat"),
        (r"\bkW\b", "kilovat"),
        (r"\bMW\b", "megavat"),
        (r"\bkV\b", "kilovolt"),
        (r"\bV\b", "volt"),
        (r"\bHz\b", "hertz"),
        (r"\bbar\b", "bar"),
        (r"\bm3/h\b", "metreküp bölü saat"),
        (r"\bm³/h\b", "metreküp bölü saat"),
        (r"\bmm\b", "milimetre"),
        (r"\bcm\b", "santimetre"),
        (r"\bkg\b", "kilogram"),
    ]

    for pattern, replacement in unit_replacements:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE,
        )

    # Temperature
    def _temperature_repl(match):
        raw = match.group(1)

        negative = raw.startswith("-")
        raw_number = raw.lstrip("-")

        if "," in raw_number:
            value = _decimal_to_tr(raw_number)
        else:
            value = _int_to_tr(int(raw_number))

        if negative:
            value = "eksi " + value

        return value + " derece santigrat"

    text = re.sub(
        r"(-?\d+(?:,\d+)?)\s*°\s*C\b",
        _temperature_repl,
        text,
        flags=re.IGNORECASE,
    )

    # Percentages
    text = re.sub(
        r"%\s*(\d+(?:,\d+)?)",
        lambda match: (
            "yüzde "
            + (
                _decimal_to_tr(match.group(1))
                if "," in match.group(1)
                else _int_to_tr(int(match.group(1)))
            )
        ),
        text,
    )

    # Currency with symbol before amount
    for symbol in ("₺", "€", "$", "£"):
        text = re.sub(
            rf"{re.escape(symbol)}\s*(\d(?:[\d.,]*\d)?)",
            lambda match, current_symbol=symbol: _currency_repl(
                current_symbol,
                match.group(1),
            ),
            text,
        )

    # Turkish lira written after amount
    text = re.sub(
        r"(\d(?:[\d.,]*\d)?)\s*TL\b",
        lambda match: _currency_repl(
            "TL",
            match.group(1),
        ),
        text,
        flags=re.IGNORECASE,
    )

    # Time HH:MM
    def _time_repl(match):
        hour = int(match.group(1))
        minute = int(match.group(2))

        if hour > 23 or minute > 59:
            return match.group(0)

        if minute == 0:
            return _int_to_tr(hour)

        return f"{_int_to_tr(hour)} {_int_to_tr(minute)}"

    text = re.sub(
        r"\b(\d{1,2}):(\d{2})\b",
        _time_repl,
        text,
    )

    # Dates DD.MM.YYYY
    def _date_repl(match):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        if not (1 <= day <= 31 and 1 <= month <= 12):
            return match.group(0)

        return (
            f"{_int_to_tr(day)} "
            f"{_MONTHS[month]} "
            f"{_int_to_tr(year)}"
        )

    text = re.sub(
        r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b",
        _date_repl,
        text,
    )

    # Turkish grouped numbers
    #
    # 1.234
    # 1.234.567
    # 1.234,56
    def _grouped_repl(match):
        raw = match.group(0)
        cleaned = raw.replace(".", "")

        if "," in cleaned:
            return _decimal_to_tr(cleaned)

        return _int_to_tr(int(cleaned))

    text = re.sub(
        r"\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b",
        _grouped_repl,
        text,
    )

    # Decimal comma
    text = re.sub(
        r"\b(\d+,\d+)\b",
        lambda match: _decimal_to_tr(
            match.group(1)
        ),
        text,
    )

    # Plain integers
    text = re.sub(
        r"\b(\d+)\b",
        lambda match: _int_to_tr(
            int(match.group(1))
        ),
        text,
    )

    # Whitespace cleanup
    text = re.sub(
        r"[ \t]{2,}",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


class TRG2P:
    """Turkish normalization + espeak-ng phonemization."""

    def __init__(self, version=None):
        # Deferred import keeps normalization unit tests
        # independent from phonemizer / espeak installation.
        from .espeak import EspeakG2P

        self.espeak = EspeakG2P(
            language="tr",
            version=version,
        )

    def __call__(self, text: str) -> Tuple[str, None]:
        normalized = normalize_text_tr(text)

        return self.espeak(normalized)
