import re

from .num2vi import n2w
from .symbol_vi import vietnamese_re

_quotes_symbol = r"(\"|\')?"
_space = r"(\s)"
_roman_number_re = r"(\b(?!LLC)(?=[MDCLXVI]+\b)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b)"
_true_letter_re = r"(chữ|chữ cái|kí tự|ký tự)" + _space + _quotes_symbol + r"([A-Z]+)" + _quotes_symbol + vietnamese_re


def _expand_roman(match):
    # from https://stackoverflow.com/questions/19308177/converting-roman-numerals-to-integers-in-python
    roman_numerals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    result = 0
    num = match.group(0).strip().rstrip()
    for i, c in enumerate(num):
        if (i + 1) == len(num) or roman_numerals[c] >= roman_numerals[num[i + 1]]:
            result += roman_numerals[c]
        else:
            result -= roman_numerals[c]
    if int(result) > 39:
        return num
    return " " + n2w(str(result)) + " "


def _not_roman_number(match):
    return match.group(0).lower()


def normalize_roman_numbers(text):
    text = re.sub(_true_letter_re, _not_roman_number, text)
    text = re.sub(_roman_number_re, _expand_roman, text)
    return text
