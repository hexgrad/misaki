# -*- coding: utf-8 -*-
'''
Special rule for processing Hangul
https://github.com/kyubyong/g2pK
'''

import re

from .utils import gloss, get_rule_id2text

rule_id2text = get_rule_id2text()


############################ vowels ############################
def jyeo(inp, descriptive=False, verbose=False):
    rule = rule_id2text["5.1"]
    # 일반적인 규칙으로 취급한다 by kyubyong

    out = re.sub("([ᄌᄍᄎ])ᅧ", r"\1ᅥ", inp)
    # gloss(verbose, out, inp, rule)
    return out


def ye(inp, descriptive=False, verbose=False):
    rule = rule_id2text["5.2"]
    # 실제로 언중은 예, 녜, 셰, 쎼 이외의 'ㅖ'는 [ㅔ]로 발음한다. by kyubyong

    if descriptive:
        out = re.sub("([ᄀᄁᄃᄄㄹᄆᄇᄈᄌᄍᄎᄏᄐᄑᄒ])ᅨ", r"\1ᅦ", inp)
    else:
        out = inp
    # gloss(verbose, out, inp, rule)
    return out


def consonant_ui(inp, descriptive=False, verbose=False):
    rule = rule_id2text["5.3"]

    out = re.sub("([ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄌᄍᄎᄏᄐᄑᄒ])ᅴ", r"\1ᅵ", inp)
    # gloss(verbose, out, inp, rule)
    return out


def josa_ui(inp, descriptive=False, verbose=False):
    rule = rule_id2text["5.4.2"]
    # 실제로 언중은 높은 확률로 조사 '의'는 [ㅔ]로 발음한다.
    if descriptive:
        out = re.sub("([^^])의/J", r"\1에", inp)
    else:
        out = inp.replace("/J", "")
    # gloss(verbose, out, inp, rule)
    return out


def vowel_ui(inp, descriptive=False, verbose=False):
    rule = rule_id2text["5.4.1"]
    # 실제로 언중은 높은 확률로 단어의 첫음절 이외의 '의'는 [ㅣ]로 발음한다."""
    if descriptive:
        out = re.sub("([^^\s]ᄋ)ᅴ", r"\1ᅵ", inp)
    else:
        out = inp
    # gloss(verbose, out, inp, rule)
    return out


def jamo(inp, descriptive=False, verbose=False):
    rule = rule_id2text["16"]
    out = inp

    out = re.sub("(디그)ᆮᄋ", r"\1ᄉ", out)
    out = re.sub("([ᄌᄎᄐᄒ]ᅵ으)[ᆽᆾᇀᇂ]ᄋ", r"\1ᄉ", out)
    out = re.sub("(키으)ᆿᄋ", r"\1ᄀ", out)
    out = re.sub("(피으)ᇁᄋ", r"\1ᄇ", out)

    # gloss(verbose, out, inp, rule)
    return out


    ############################ 어간 받침 ############################
def rieulgiyeok(inp, descriptive=False, verbose=False):
    rule = rule_id2text["11.1"]

    out = inp
    out = re.sub("ᆰ/P([ᄀᄁ])", r"ᆯᄁ", out)

    # gloss(verbose, out, inp, rule)
    return out


def rieulbieub(inp, descriptive=False, verbose=False):
    rule = rule_id2text["25"]
    out = inp

    out = re.sub("([ᆲᆴ])/Pᄀ", r"\1ᄁ", out)
    out = re.sub("([ᆲᆴ])/Pᄃ", r"\1ᄄ", out)
    out = re.sub("([ᆲᆴ])/Pᄉ", r"\1ᄊ", out)
    out = re.sub("([ᆲᆴ])/Pᄌ", r"\1ᄍ", out)

    # gloss(verbose, out, inp, rule)
    return out


def verb_nieun(inp, descriptive=False, verbose=False):
    rule = rule_id2text["24"]
    out = inp

    pairs = [ ("([ᆫᆷ])/Pᄀ", r"\1ᄁ"),
              ("([ᆫᆷ])/Pᄃ", r"\1ᄄ"),
              ("([ᆫᆷ])/Pᄉ", r"\1ᄊ"),
              ("([ᆫᆷ])/Pᄌ", r"\1ᄍ"),

              ("ᆬ/Pᄀ", "ᆫᄁ"),
              ("ᆬ/Pᄃ", "ᆫᄄ"),
              ("ᆬ/Pᄉ", "ᆫᄊ"),
              ("ᆬ/Pᄌ", "ᆫᄍ"),

              ("ᆱ/Pᄀ", "ᆷᄁ"),
              ("ᆱ/Pᄃ", "ᆷᄄ"),
              ("ᆱ/Pᄉ", "ᆷᄊ"),
              ("ᆱ/Pᄌ", "ᆷᄍ")  ]

    for str1, str2 in pairs:
        out = re.sub(str1, str2, out)

    # gloss(verbose, out, inp, rule)
    return out


def balb(inp, descriptive=False, verbose=False):
    rule = rule_id2text["10.1"]
    out = inp
    syllable_final_or_consonants = "($|[^ᄋᄒ])"

    # exceptions
    out = re.sub(f"(바)ᆲ({syllable_final_or_consonants})", r"\1ᆸ\2", out)
    out = re.sub(f"(너)ᆲ([ᄌᄍ]ᅮ|[ᄃᄄ]ᅮ)", r"\1ᆸ\2", out)
    # gloss(verbose, out, inp, rule)
    return out


def palatalize(inp, descriptive=False, verbose=False):
    rule = rule_id2text["17"]
    out = inp

    out = re.sub("ᆮᄋ([ᅵᅧ])", r"ᄌ\1", out)
    out = re.sub("ᇀᄋ([ᅵᅧ])", r"ᄎ\1", out)
    out = re.sub("ᆴᄋ([ᅵᅧ])", r"ᆯᄎ\1", out)

    out = re.sub("ᆮᄒ([ᅵ])", r"ᄎ\1", out)

    # gloss(verbose, out, inp, rule)
    return out


def modifying_rieul(inp, descriptive=False, verbose=False):
    rule = rule_id2text["27"]
    out = inp
    
    pairs = [   
                # ("ᆯ/E ᄀ", r"ᆯ ᄁ"),
                # ("ᆯ/E ᄃ", r"ᆯ ᄄ"),
                # ("ᆯ/E ᄇ", r"ᆯ ᄈ"),
                # ("ᆯ/E ᄉ", r"ᆯ ᄊ"),
                # ("ᆯ/E ᄌ", r"ᆯ ᄍ"),

                ("ᆯ걸", "ᆯ껄"),
                ("ᆯ밖에", "ᆯ빠께"),
                ("ᆯ세라", "ᆯ쎄라"),
                ("ᆯ수록", "ᆯ쑤록"),
                ("ᆯ지라도", "ᆯ찌라도"),
                ("ᆯ지언정", "ᆯ찌언정"),
                ("ᆯ진대", "ᆯ찐대") ]

    for str1, str2 in pairs:
        out = re.sub(str1, str2, out)

    # gloss(verbose, out, inp, rule)
    return out
