import re
import json
from pathlib import Path

_letter_to_arpabet = {
    "A": "EY1",
    "B": "B IY1",
    "C": "S IY1",
    "D": "D IY1",
    "E": "IY1",
    "F": "EH1 F",
    "G": "JH IY1",
    "H": "EY1 CH",
    "I": "AY1",
    "J": "JH EY1",
    "K": "K EY1",
    "L": "EH1 L",
    "M": "EH1 M",
    "N": "EH1 N",
    "O": "OW1",
    "P": "P IY1",
    "Q": "K Y UW1",
    "R": "AA1 R",
    "S": "EH1 S",
    "T": "T IY1",
    "U": "Y UW1",
    "V": "V IY1",
    "X": "EH1 K S",
    "Y": "W AY1",
    "W": "D AH1 B AH0 L Y UW0",
    "Z": "Z IY1",
    "s": "Z",
}

# Acronyms that should not be expanded
hardcoded_acronyms = [
    "BMW",
    "MVD",
    "WDSU",
    "GOP",
    "UK",
    "AI",
    "GPS",
    "BP",
    "FBI",
    "HD",
    "CES",
    "LRA",
    "PC",
    "NBA",
    "BBL",
    "OS",
    "IRS",
    "SAC",
    "UV",
    "CEO",
    "TV",
    "CNN",
    "MSS",
    "GSA",
    "USSR",
    "DNA",
    "PRS",
    "TSA",
    "US",
    "GPU",
    "USA",
    "FPCC",
    "CIA",
    "WTO",
    "WHO",
    "WB",
    "IMF",
    "UN",
    "AFC",
    "APEC",
    "IAEA",
    "ICC",
    "AFF",
    "GPRS",
    "BBC",
    "IQ",
    "EQ",
]

# Words and acronyms that should be read as regular words, e.g., NATO, HAPPY, etc.
uppercase_whiteliset = []

acronyms_exceptions = {
    "NVIDIA": "N.VIDIA",
}

acronyms_exceptions_vi = {
    "CĐV": "cổ động viên",
    "TV": "ti vi",
    "HĐND": "hội đồng nhân dân",
    "TAND": "toàn án nhân dân",
    "BHXH": "bảo hiểm xã hội",
    "BHTN": "bảo hiểm thất nghiệp",
    "TP.HCM": "thành phố hồ chí minh",
    "VN": "việt nam",
    "BCHTW": "ban chấp hành trung ương",
    "UBND": "uỷ ban nhân dân",
    "TPHCM": "thành phố hồ chí minh",
    "TP": "thành phố",
    "HCM": "hồ chí minh",
    "SG": "Sài Gòn",
    "HN": "hà nội",
    "BTC": "ban tổ chức",
    "CLB": "câu lạc bộ",
    "HTX": "hợp tác xã",
    "NXB": "nhà xuất bản",
    "ÔBA": "ông bà",
    "QLTT": "quản lý thị trường",
    "BST": "bộ sưu tập",
    "TTTM": "trung tâm thương mại",
    " TT ": " thủ tướng ",
    "TW": "trung ương",
    "GD-ĐT": "giáo dục và đào tạo",
    "BCH": "bản chấp hành",
    "CHXHCNVN": "cộng hòa xã hội chủ nghĩa việt nam",
    "CSGT": "cảnh sát giao thông",
    "MTDTGPMNVN": "mặt trận dân tộc giải phóng miền nam Việt Nam",
    "QDND": "quân đội nhân dân",
    "QLVNCH": "quân lực việt nam cộng hòa",
    "VNCH": "việt nam cộng hòa",
    "LHQ": "liên hợp quốc",
    "UBKT": "uỷ ban kinh tế",
    "THCS": "trung học cơ sở",
    "THPT": "trung học phổ thông",
    "THPTQG": "trung học phổ thông quốc gia",
    "ĐH": "đại học",
    "HLV": "huấn luyện viên",
    "PGS.": "phó giáo sư",
    "PGS": "phó giáo sư",
    "P.GS.": "phó giáo sư",
    "P.GS": "phó giáo sư",
    "GS.": "giáo sư",
    "GS": "giáo sư",
    "ThS.": "thạc sĩ",
    "ThS": "thạc sĩ",
    "TS.": "tiến sĩ",
    "TS": "tiến sĩ",
    "TNHH": "trách nhiệm hữu hạn",
    "CSKH": "chăm sóc khách hàng",
    "VĐV": "vận động viên",
    "NSND": "nghệ sĩ nhân dân",
    "NSƯT": "nghệ sĩ ưu tú",
    "PCCC": "phòng cháy chữa cháy",
    "PGĐ": "phó giám đốc",
    "GĐ": "giám đốc",
    "TPHCM": "thành phố hồ chí minh",
    "BS": "bác sỹ",
    "GDP": "gi đi pi",
    "FDI": "ép đê i",
    "ODA": "ô đê a",
    "VKSND": "viện kiểm soát nhân dân",
    "HĐXX": "hội đồng xét xử",
    "TTXVN": "thông tấn xã việt nam",
    "F và B": "ép èn bi",
    "1-0-2": "một không hai",
    "SN": "sinh năm",
    "môtô": "mô tô",
    "ôtô": "ô tô",
    "êkip": "ê kíp",
    "youtube": "du túp",
    "facebook": "phây búc",
    "tiktok": "tíc tót",
    "KQXS": "kết quả sổ xố",
    "XSMB": "xổ số miền bắc",
    "XSMN": "xổ số miền nam",
    "XSMT": "xổ số miền tây",
    "sars-cov":"sát cô vi",
    "covid":"cô vít",
    "coronavirus": "cô rô na vai rớt"
}
acronyms_exceptions_vi.update(
    json.loads(Path(__file__, '..', '..', 'data', 'vi_acronyms.json').resolve().read_text(encoding="utf-8"))
)

non_uppercase_exceptions = {
    "email": "e-mail",
}

# must ignore roman numerals
_acronym_re = re.compile(r"([a-z]*[A-Z][A-Z]+)s?\.?")


# def _expand_acronyms_to_arpa(m, add_spaces=True):
#     acronym = m.group(0)

#     # remove dots if they exist
#     acronym = re.sub('', '', acronym)

#     acronym = "".join(acronym.split())
#     arpabet = cmudict.lookup(acronym)

#     if arpabet is None:
#         acronym = list(acronym)
#         arpabet = [
#             "{" + _letter_to_arpabet[letter] + "}" for letter in acronym]
#         # temporary fix
#         if arpabet[-1] == '{Z}' and len(arpabet) > 1:
#             arpabet[-2] = arpabet[-2][:-1] + ' ' + arpabet[-1][1:]
#             del arpabet[-1]

#         arpabet = ' '.join(arpabet)
#     elif len(arpabet) == 1:
#         arpabet = "{" + arpabet[0] + "}"
#     else:
#         arpabet = acronym

#     return arpabet


# def normalize_acronyms(text):
#     text = re.sub(_acronym_re, _expand_acronyms_to_arpa, text)
#     return text


def expand_acronyms(m):
    text = m.group(1)
    if text in hardcoded_acronyms:
        text = [word for word in m.group(0)]
        text = "  ".join(text)
        return text
    else:
        return text


def expand_acronyms_vi(text):
    for k, v in acronyms_exceptions_vi.items():
        text = re.sub(r"\b" + k + r"\b", v, text, flags=re.IGNORECASE)
    return text
    # else:
    #     text = '.'.join(text) + '.'

    # if text[-1] != '.' and m.group(0)[-1] == '.':
    #     return text + '.'
    # else:
    #     return text


def spell_acronyms_vi(text):
    text = expand_acronyms_vi(text)
    text = re.sub(_acronym_re, expand_acronyms, text)
    return text
