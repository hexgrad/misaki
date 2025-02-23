# -*- coding: utf-8 -*-
'''
Convert English to Hangul
https://github.com/kyubyong/g2pK
'''

import re

from .utils import adjust, compose, to_choseong, to_jungseong, to_jongseong, reconstruct


eng2kor = {
    'A': '에이',
    'B': '비',
    'C': '씨',
    'D': '디',
    'E': '이',
    'F': '에프',
    'G': '지',
    'H': '에이치',
    'I': '아이',
    'J': '제이',
    'K': '케이',
    'L': '엘',
    'M': '엠',
    'N': '엔',
    'O': '오',
    'P': '피',
    'Q': '큐',
    'R': '알',
    'S': '에스',
    'T': '티',
    'U': '유',
    'V': '브이',
    'W': '더블유',
    'X': '엑스',
    'Y': '와이',
    'Z': '지',
}


def word_to_hangul(word):
    ret = ''
    for alpha in word:
        ret += eng2kor[alpha]
    return ret

def convert_eng(string, cmu):
    '''Convert a string such that English words inside are turned into Hangul.
    string: input string.
    cmu: cmu dict object.

    >>> convert_eng("그 사람 좀 old school이야", cmu)
    그 사람 좀 올드 스쿨이야
    '''
    eng_words = list(set(re.findall("[A-Za-z]+", string)))
    for eng_word in sorted(eng_words, key=len, reverse=True):
        print('eng_word :', eng_word)
        if eng_word.isupper() or (eng_word.lower() not in cmu):
            ret = word_to_hangul(eng_word.upper())
            string = string.replace(eng_word, ret)
            print(eng_word, ret)
            continue

        word = eng_word.lower()
        arpabets = cmu[word][0] # https://en.wikipedia.org/wiki/ARPABET
        phonemes = adjust(arpabets)
        ret = ""
        for i in range(len(phonemes)):
            p = phonemes[i] # phoneme
            p_prev = phonemes[i - 1] if i > 0 else "^"
            p_next = phonemes[i + 1] if i < len(phonemes) - 1 else "$"
            p_next2 = phonemes[i + 1] if i < len(phonemes) - 2 else "$"

            # desginated sets
            short_vowels = ("AE", "AH", "AX", "EH", "IH", "IX", "UH")
            vowels = "AEIOUY"
            consonants = "BCDFGHJKLMNPQRSTVWXZ"
            syllable_final_or_consonants = "$BCDFGHJKLMNPQRSTVWXZ"

            # 외래어 표기법 https://ko.dict.naver.com/help.nhn?page=4-1-3-1#dtl_cts
            #  1항. 무성 파열음 ([p], [t], [k])
            # 1. 짧은 모음 다음의 어말 무성 파열음([p], [t], [k])은 받침으로 적는다.
            # 2. 짧은 모음과 유음·비음([l], [r], [m], [n]) 이외의 자음 사이에 오는 무성 파열음([p], [t], [k])은 받침으로 적는다.
            # 3. 위 경우 이외의 어말과 자음 앞의 [p], [t], [k]는 '으'를 붙여 적는다.

            if p in "PTK":
                if p_prev[:2] in short_vowels and p_next == "$":  # 1
                    ret += to_jongseong(p)
                elif p_prev[:2] in short_vowels and p_next[0] not in "AEIOULRMN":  # 2
                    ret += to_jongseong(p)
                elif p_next[0] in "$BCDFGHJKLMNPQRSTVWXYZ":  # 3
                    ret += to_choseong(p)
                    ret += "ᅳ"
                else:
                    ret += to_choseong(p)

            # 2항. 유성 파열음([b], [d], [g])
            # 어말과 모든 자음 앞에 오는 유성 파열음은 '으'를 붙여 적는다.
            elif p in "BDG":
                ret += to_choseong(p)
                if p_next[0] in syllable_final_or_consonants:
                    ret += "ᅳ"

            # 3항. 마찰음([s], [z], [f], [v], [θ], [ð], [ʃ], [ʒ])
            # 1. 어말 또는 자음 앞의 [s], [z], [f], [v], [θ], [ð]는 '으'를 붙여 적는다.
            # 2. 어말의 [ʃ]는 '시'로 적고, 자음 앞의 [ʃ]는 '슈'로, 모음 앞의 [ʃ]는 뒤따르는 모음에 따라 '샤', '섀', '셔', '셰', '쇼', '슈', '시'로 적는다.
            # 3. 어말 또는 자음 앞의 [ʒ]는 '지'로 적고, 모음 앞의 [ʒ]는 'ㅈ'으로 적는다.
            elif p in ("S", "Z", "F", "V", "TH", "DH", "SH", "ZH"):
                ret += to_choseong(p)

                if p in ("S", "Z", "F", "V", "TH", "DH"):  # 1
                    if p_next[0] in syllable_final_or_consonants:
                        ret += "ᅳ"
                elif p == "SH":  # 2
                    if p_next[0] in "$":
                        ret += "ᅵ"
                    elif p_next[0] in consonants:
                        ret += "ᅲ"
                    else:
                        ret += "Y"
                elif p == "ZH":  # 3
                    if p_next[0] in syllable_final_or_consonants:
                        ret += "ᅵ"

            # 4항. 파찰음([ʦ], [ʣ], [ʧ], [ʤ])
            # 1. 어말 또는 자음 앞의 [ʦ], [ʣ]는 '츠', '즈'로 적고, [ʧ], [ʤ]는 '치', '지'로 적는다.
            # 2. 모음 앞의 [ʧ], [ʤ]는 'ㅊ', 'ㅈ'으로 적는다.
            elif p in ("TS", "DZ", "CH", "JH",):
                ret += to_choseong(p)  # 2

                if p_next[0] in syllable_final_or_consonants:  # 1
                    if p in ("TS", "DZ"):
                        ret += "ᅳ"
                    else:
                        ret += "ᅵ"

            # 5항. 비음([m], [n], [ŋ])
            # 1. 어말 또는 자음 앞의 비음은 모두 받침으로 적는다.
            # 2. 모음과 모음 사이의 [ŋ]은 앞 음절의 받침 'ㆁ'으로 적는다.
            elif p in ("M", "N", "NG"):
                if p in "MN" and p_next[0] in vowels:
                    ret += to_choseong(p)
                else:
                    ret += to_jongseong(p)

            # 6항. 유음([l])
            # 1. 어말 또는 자음 앞의 [l]은 받침으로 적는다.
            # 2. 어중의 [l]이 모음 앞에 오거나, 모음이 따르지 않는 비음([m], [n]) 앞에 올 때에는 'ㄹㄹ'로 적는다.
            # 3. 다만, 비음([m], [n]) 뒤의 [l]은 모음 앞에 오더라도 'ㄹ'로 적는다.
            elif p == "L":
                if p_prev == "^":  # initial
                    ret += to_choseong(p)
                elif p_next[0] in "$BCDFGHJKLPQRSTVWXZ":  # 1
                    ret += to_jongseong(p)
                elif p_prev in "MN":  # 3
                    ret += to_choseong(p)
                elif p_next[0] in vowels:  # 2
                    ret += "ᆯᄅ"
                elif p_next in "MN" and p_next2[0] not in vowels:  # 2
                    ret += "ᆯ르"

            # custom
            elif p == "ER":
                if p_prev[0] in vowels:
                    ret += "ᄋ"
                ret += to_jungseong(p)
                if p_next[0] in vowels:
                    ret += "ᄅ"
            elif p == "R":
                if p_next[0] in vowels:
                    ret += to_choseong(p)

            # 8항. 중모음1) ([ai], [au], [ei], [ɔi], [ou], [auə])
            # 중모음은 각 단모음의 음가를 살려서 적되, [ou]는 '오'로, [auə]는 '아워'로 적는다.
            elif p[0] in "AEIOU":
                ret += to_jungseong(p)

            else:
                ret += to_choseong(p)

        ret = reconstruct(ret)
        ret = compose(ret)
        ret = re.sub("[\u1100-\u11FF]", "", ret) # remove hangul jamo
        string = string.replace(eng_word, ret)
    return string

if __name__ == "__main__":
    from nltk.corpus import cmudict
    cmu = cmudict.dict()
    print(convert_eng("오늘 학교에서 밥을 먹고 집에 와서 game을 했다", cmu))