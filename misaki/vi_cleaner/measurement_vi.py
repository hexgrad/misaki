import re
from .symbol_vi import vietnamese_re, vietnamese_without_num_re

_measurement_key_vi = {
    "p": "phút",
    "s": "giây",
    "TB": "tê ra bai",
    "GB": "gi ga bai",
    "MB": "mê ga bai",
    "KB": "ki lô bai",
    "Kb": "ki lô bai",
    "b": "bai",
    "GHz": "gi ga héc",
    "MHz": "mê ga héc",
    "mHz": "mi li héc",
    "kHz": "ki lô héc",
    "nHz": "na nô héc",
    "hz": "héc",
    "Hz": "héc",
    "m2": "mét vuông",
    "km2": "ki lô mét vuông",
    "m3": "mét khối",
    "km3": "ki lô mét khối",
    "nm": "na nô mét",
    "mm": "mi li mét",
    "cm": "xen ti mét",
    "dm": "đề xi mét",
    "dam": "đề ca mét",
    "hm": "héc tô mét",
    "km": "ki lô mét",
    "kg": "ki lô gam",
    "hg": "héc tô gam",
    "dag": "đề ca gam",
    "mg": "mi li gam",
    "ml": "mi li lít",
    "l": "lít",
    "L": "lít",
    "g": "gam",
    "m": "mét",
    "in": "inch",
    "h": "giờ",
    "ha": "héc ta",
}

_measurement_combine_regex = "|".join(_measurement_key_vi.keys())
_measurement_pattern = re.compile(vietnamese_without_num_re + "(" + _measurement_combine_regex + ")" + vietnamese_re)
_measurement_with_splash_pattern = re.compile(vietnamese_without_num_re + "(" + _measurement_combine_regex + ")(/)(" + _measurement_combine_regex + ")" + vietnamese_re)


def _expand_measurement_vi(match):
    prefix, measure, suffix = match.groups(0)
    if len(measure) == 1 and not prefix.isdigit():
        return match.group(0)
    measure = _measurement_key_vi[measure]
    return prefix + " " + measure + " " + suffix


def _expand_measurement_with_splash_vi(match):
    prefix, measure1, splash, measure2, suffix = match.groups(0)
    measure1 = _measurement_key_vi[measure1]
    measure2 = _measurement_key_vi[measure2]
    return prefix + " " + measure1 + " trên " + measure2 + suffix


def normalize_measurement_vi(text):
    text = re.sub(_measurement_with_splash_pattern, _expand_measurement_with_splash_vi, text)
    text = re.sub(_measurement_pattern, _expand_measurement_vi, text)
    return text
