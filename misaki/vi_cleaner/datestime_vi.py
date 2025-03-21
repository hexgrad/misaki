import re

from vietnam_number.number2word import n2w
from .symbol_vi import vietnamese_re, vietnamese_for_date_re
from .roman_number_vi import normalize_roman_numbers

day_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_date_seperator = r"(\/|-|\.)"

_day_periods = r"(ngày|hôm|sáng|trưa|chiều|tối|đêm|khuya)"

_roman_or_number_quarter_re = r"(\d{1,2}|(I|II|III|IV))"

_quarter_month_year_pattern = r"(quý)" + vietnamese_re + _roman_or_number_quarter_re + \
    _date_seperator + r"(\d{4})" + vietnamese_for_date_re

_full_date_pattern = r"(ngày)?" + vietnamese_re + r"(\d{1,2})" + _date_seperator + \
    r"(\d{1,2})" + _date_seperator + r"(\d{4})" + vietnamese_for_date_re
_full_range_date_pattern = r"(ngày)?" + vietnamese_re + r"(\d{1,2})(\-)(\d{1,2})" + \
    _date_seperator + r"(\d{1,2})" + _date_seperator + \
    r"(\d{4})" + vietnamese_for_date_re

_day_month_pattern = _day_periods + vietnamese_re + \
    r"(\d{1,2})" + _date_seperator + r"(\d{1,2})" + vietnamese_for_date_re
_range_day_month_pattern = r"(ngày)?" + vietnamese_re + \
    r"(\d{1,2})(\-)(\d{1,2})" + _date_seperator + \
    r"(\d{1,2})" + vietnamese_for_date_re

_month_year_pattern = r"(tháng)?" + vietnamese_re + \
    r"(\d{1,2})" + _date_seperator + r"(\d{4})" + vietnamese_for_date_re
_range_month_year_pattern = r"(tháng)?" + vietnamese_re + \
    r"(\d{1,2})(\-)(\d{1,2})" + _date_seperator + \
    r"(\d{4})" + vietnamese_for_date_re

_full_time_pattern = vietnamese_re + \
    r"(\d{1,2})(g|:|h)(\d{1,2})(p|:|m)(\d{1,2})(s|g)?" + vietnamese_for_date_re
_time_pattern = vietnamese_re + \
    r"(\d{1,2})(g|:|h)(\d{1,2})(p|m)?" + vietnamese_for_date_re


def _remove_prefix_zero(text):
    text = text.strip().rstrip()
    while len(text) > 0 and text[0] == "0" and (len(text) > 1 and text[1] != ","):
        text = text[1:]
    return text if (len(text) > 0) else "0"


def _is_valid_quarter(quarter):
    return quarter in range(1, 5)


def _is_valid_date(day, month):
    return month in range(1, 13) and day in range(1, day_in_month[month - 1] + 1)


def _is_valid_time(hour, minute, second=0):
    return hour in range(24) and minute in range(60) and second in range(60)


def _expand_full_date(match):
    prefix, space, day, seporator1, month, seporator2, year, suffix = match.groups(
        0)
    space = "" if space == 0 else space
    day = _remove_prefix_zero(day)
    month = _remove_prefix_zero(month)
    year = _remove_prefix_zero(year)
    if not _is_valid_date(int(day), int(month)) or prefix == seporator1:
        return match.group(0)
    return space + " ngày " + n2w(day) + " tháng " + n2w(month) + " năm " + n2w(year) + suffix + " "


def _expand_range_full_date(match):
    prefix, space, day_start, hypen, day_end, seporator1, month, seporator2, year, suffix = match.groups(
        0)
    space = "" if space == 0 else space
    day_start = _remove_prefix_zero(day_start)
    day_end = _remove_prefix_zero(day_end)
    month = _remove_prefix_zero(month)
    year = _remove_prefix_zero(year)
    month = _remove_prefix_zero(month)
    if not _is_valid_date(int(day_start), int(month)) or not _is_valid_date(int(day_end), int(month)):
        return match.group(0)
    return space + " ngày " + n2w(day_start) + " đến ngày " + n2w(day_end) + " tháng " + n2w(month) + " năm " + n2w(year) + suffix + " "


def _expand_day_month(match):
    prefix, space, day, seporator1, month, suffix = match.groups(0)
    prefix = prefix + " ngày" if prefix != "ngày" else prefix
    space = "" if space == 0 else space
    day = _remove_prefix_zero(day)
    month = _remove_prefix_zero(month)
    if not _is_valid_date(int(day), int(month)) or space == seporator1:
        return match.group(0)
    return space + prefix + space + n2w(day) + " tháng " + n2w(month) + suffix + " "


def _expand_range_day_month(match):
    prefix, space, day_start, hypen, day_end, seporator1, month, suffix = match.groups(
        0)
    space = "" if space == 0 else space
    day_start = _remove_prefix_zero(day_start)
    day_end = _remove_prefix_zero(day_end)
    month = _remove_prefix_zero(month)
    if not _is_valid_date(int(day_start), int(month)) or not _is_valid_date(int(day_end), int(month)):
        return match.group(0)
    return space + " ngày " + n2w(day_start) + " đến ngày " + n2w(day_end) + " tháng " + n2w(month) + suffix + " "


def _expand_month_year(match):
    prefix, space, month, seporator, year, suffix = match.groups(0)
    space = "" if space == 0 else space
    month = _remove_prefix_zero(month)
    year = _remove_prefix_zero(year)
    if not _is_valid_date(1, int(month)) or space == seporator:
        return match.group(0)
    return space + " tháng " + n2w(month) + " năm " + n2w(year) + suffix + " "


def _expand_quarter_month_year(match):
    _, space, quarter, _, seporator, year, suffix = match.groups(0)
    space = "" if space == 0 else space
    try:
        quarter = _remove_prefix_zero(quarter)
        quarter_string = n2w(quarter)
    except:
        quarter_string = normalize_roman_numbers(quarter)
    year = _remove_prefix_zero(year)
    if quarter not in ["I", "II", "III", "IV"]:
        if not _is_valid_quarter(int(quarter)) or space == seporator:
            return match.group(0)
    return space + " quý " + quarter_string + " năm " + n2w(year) + suffix + " "


def _expand_range_month_year(match):
    prefix, space, month_start, hypen, month_end, seporator, year, suffix = match.groups(
        0)
    space = "" if space == 0 else space
    month_start = _remove_prefix_zero(month_start)
    month_end = _remove_prefix_zero(month_end)
    year = _remove_prefix_zero(year)
    if not _is_valid_date(1, int(month_start)) or not _is_valid_date(1, int(month_end)) or hypen == seporator:
        return match.group(0)
    return space + " tháng " + n2w(month_start) + " đến tháng " + n2w(month_end) + " năm " + n2w(year) + suffix + " "


def _expand_time(math):
    prefix, hour, seporator, minute, suffix, ending_space = math.groups(0)
    prefix = "" if prefix == 0 else prefix
    hour = _remove_prefix_zero(hour)
    minute = _remove_prefix_zero(minute)
    if not _is_valid_time(int(hour), int(minute)):
        return math.group(0)
    return prefix + " " + n2w(hour) + " giờ " + n2w(minute) + " phút" + ending_space + " "


def _expand_full_time(math):
    prefix, hour, seporator1, minute, seporator2, second, suffix, ending_space = math.groups(
        0)
    prefix = "" if prefix == 0 else prefix
    hour = _remove_prefix_zero(hour)
    minute = _remove_prefix_zero(minute)
    second = _remove_prefix_zero(second)
    if not _is_valid_time(int(hour), int(minute), int(second)):
        return math.group(0)
    return prefix + " " + n2w(hour) + " giờ " + n2w(minute) + " phút " + n2w(second) + " giây" + ending_space + " "


def normalize_date(text):
    text = re.sub(_quarter_month_year_pattern, _expand_quarter_month_year,
                  text, flags=re.IGNORECASE)
    text = re.sub(_range_month_year_pattern,
                  _expand_range_month_year, text, flags=re.IGNORECASE)
    text = re.sub(_full_range_date_pattern,
                  _expand_range_full_date, text, flags=re.IGNORECASE)
    text = re.sub(_full_date_pattern, _expand_full_date,
                  text, flags=re.IGNORECASE)
    text = re.sub(_month_year_pattern, _expand_month_year,
                  text, flags=re.IGNORECASE)
    text = re.sub(_range_day_month_pattern,
                  _expand_range_day_month, text, flags=re.IGNORECASE)
    text = re.sub(_day_month_pattern, _expand_day_month,
                  text, flags=re.IGNORECASE)
    return text


def normalize_time(text):
    text = re.sub(_full_time_pattern, _expand_full_time,
                  text, flags=re.IGNORECASE)
    text = re.sub(_time_pattern, _expand_time, text, flags=re.IGNORECASE)
    return text
