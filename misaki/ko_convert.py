from typing import List, Tuple, Optional
from collections import Counter

# 자모 IPA 매핑 테이블
jamo_to_ipa = {
    # 모음
    'ㅏ': 'a', 'ㅐ': 'ɛ', 'ㅑ': 'ja', 'ㅒ': 'jɛ', 'ㅓ': 'ʌ',
    'ㅔ': 'e', 'ㅕ': 'jʌ', 'ㅖ': 'jɛ', 'ㅗ': 'o', 'ㅘ': 'wa',
    'ㅙ': 'wɛ', 'ㅚ': 'ø', 'ㅛ': 'jo', 'ㅜ': 'u', 'ㅝ': 'wʌ',
    'ㅞ': 'we', 'ㅟ': 'y', 'ㅠ': 'ju', 'ㅡ': 'ɯ', 'ㅢ': 'ɯi',
    'ㅣ': 'i',
}

# 초성 IPA 매핑
initial_jamo_to_ipa = {
    'ㄱ': 'k', 'ㄲ': 'k͈', 'ㄴ': 'n', 'ㄷ': 't', 'ㄸ': 't͈',
    'ㄹ': 'l', 'ㅁ': 'm', 'ㅂ': 'p', 'ㅃ': 'p͈', 'ㅅ': 's',
    'ㅆ': 's͈', 'ㅇ': '',  # 초성 'ㅇ'은 무음
    'ㅈ': 'tɕ', 'ㅉ': 'tɕ͈', 'ㅊ': 'tɕʰ',
    'ㅋ': 'kʰ', 'ㅌ': 'tʰ', 'ㅍ': 'pʰ', 'ㅎ': 'h',
}

# 종성 IPA 매핑
final_jamo_to_ipa = {
    'ㄱ': 'k̚', 'ㄲ': 'k̚',  # 불파음으로 통일
    'ㄴ': 'n', 'ㄷ': 't̚', 'ㄸ': 't̚',
    'ㄹ': 'l', 'ㅁ': 'm',
    'ㅂ': 'p̚', 'ㅃ': 'p̚',
    'ㅅ': 't̚', 'ㅆ': 't̚',
    'ㅇ': 'ŋ',
    'ㅈ': 't̚', 'ㅉ': 't̚', 'ㅊ': 't̚',
    'ㅋ': 'k̚', 'ㅌ': 't̚', 'ㅍ': 'p̚', 'ㅎ': 't̚',
    # 복합 종성
    'ㄳ': 'k̚', 'ㄵ': 'n', 'ㄶ': 'n',
    'ㄺ': 'k̚', 'ㄻ': 'm', 'ㄼ': 'l',
    'ㄽ': 'l', 'ㄾ': 'l', 'ㄿ': 'l',
    'ㅀ': 'l', 'ㅄ': 'p̚'
}

def decompose_hangul(char: str) -> Tuple[str, str, str]:
    """한글 문자를 초성/중성/종성으로 분해"""
    if not '가' <= char <= '힣':
        return ('', '', '')
        
    cho_list = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    jung_list = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
    jong_list = ['', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
    
    code = ord(char) - ord('가')
    cho = cho_list[code // (21 * 28)]
    jung = jung_list[(code % (21 * 28)) // 28]
    jong_idx = code % 28
    jong = jong_list[jong_idx] if jong_idx > 0 else ''
    
    return (cho, jung, jong)

def text_to_ipa(text: str) -> List[str]:
    """한글 텍스트를 IPA 음소 리스트로 변환"""
    ipa_phonemes = []
    
    # 문장 부호와 공백 처리를 위한 매핑
    punctuation_map = {
        '.': '.',
        '!': '!',
        '?': '?',
        ',': ',',
        ' ': ' '
    }
    
    for char in text:
        if char in punctuation_map:
            ipa_phonemes.append(punctuation_map[char])
            continue
            
        if '가' <= char <= '힣':
            cho, jung, jong = decompose_hangul(char)
            
            # 초성 변환
            if cho:
                ipa_initial = initial_jamo_to_ipa.get(cho)
                if ipa_initial:
                    ipa_phonemes.append(ipa_initial)
            
            # 중성 변환
            if jung:
                ipa_vowel = jamo_to_ipa.get(jung)
                if ipa_vowel:
                    ipa_phonemes.append(ipa_vowel)
            
            # 종성 변환
            if jong:
                ipa_final = final_jamo_to_ipa.get(jong)
                if ipa_final:
                    ipa_phonemes.append(ipa_final)
    
    return ipa_phonemes

def convert(text: str) -> str:
    """기존 convert 함수"""
    from ko_convert import convert as original_convert
    return original_convert(text)

def convert2(text: str) -> str:
    """새로운 convert 함수 - IPA 변환"""
    result = []
    for char in text:
        if '가' <= char <= '힣':
            cho, jung, jong = decompose_hangul(char)
            
            # 초성 변환
            if cho:
                ipa_initial = initial_jamo_to_ipa.get(cho)
                if ipa_initial:
                    result.append(ipa_initial)
            
            # 중성 변환
            if jung:
                ipa_vowel = jamo_to_ipa.get(jung)
                if ipa_vowel:
                    result.append(ipa_vowel)
            
            # 종성 변환
            if jong:
                ipa_final = final_jamo_to_ipa.get(jong)
                if ipa_final:
                    result.append(ipa_final)
        else:
            result.append(char)
    
    return ''.join(result)  # 리스트를 문자열로 결합하여 반환

# 사용 예시
if __name__ == "__main__":
    test_text = "안녕하세요!"
    ipa_result = text_to_ipa(test_text)
    print(f"입력 텍스트: {test_text}")
    print(f"IPA 변환 결과: {' '.join(ipa_result)}")