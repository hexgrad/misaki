# -*- coding: utf-8 -*-
from pypinyin import lazy_pinyin, Style
from .transcription import pinyin_to_ipa
import re
import cn2an

class ZHG2P:

    punctuations = r'[，、：；。！？]'
    punctuation_replacements = {
            '，': ' | ',
            '、': ' | ',
            '：': ' | ',
            '；': ' ‖ ‖ ',
            '。': ' ‖ ‖ ‖ ',
            '！': ' ‖ ‖ ‖ ', 
            '？': ' ‖ ‖ ‖ ', 
    }

    def replace_punctuation(self, match):
        return self.punctuation_replacements[match.group()]    

    @classmethod
    def retone(cls, p):
        p = p.replace('˧˩˧', '↓') # third tone
        p = p.replace('˧˥', '↗')  # second tone
        p = p.replace('˥˩', '↘')  # fourth tone
        p = p.replace('˥', '→')   # first tone
        p = p.replace(chr(635)+chr(809), 'ɨ').replace(chr(633)+chr(809), 'ɨ')
        assert chr(809) not in p, p
        return p

    @classmethod
    def py2ipa(cls, py):
        return ''.join(cls.retone(p) for p in pinyin_to_ipa(py)[0])

    @classmethod
    def word2ipa(cls, w):
        pinyins = lazy_pinyin(w, style=Style.TONE3, neutral_tone_with_five=True)
        return ''.join(cls.py2ipa(py) for py in pinyins)

    def __call__(self, text, zh='\u4E00-\u9FFF'):
        if not text:
            return ''
        punctuation_pattern = re.compile(self.punctuations)
        replace_punctuation = self.replace_punctuation        
        is_zh = re.match(f'[{zh}]', text[0])
        result = ''
        zhstr = cn2an.transform(text, "an2cn")
        for segment in re.findall(f'[{zh}]+|[^{zh}]+', zhstr):
            # print(is_zh, segment)
            if is_zh:
                words = [segment]
                segment = ' '.join(type(self).word2ipa(w) for w in words)
            else:
                segment = re.sub(punctuation_pattern, replace_punctuation, segment)
            result += segment
            is_zh = not is_zh
        return result.replace(chr(815), '')
