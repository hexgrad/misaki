from .transcription import pinyin_to_ipa
from pypinyin import lazy_pinyin, Style
import cn2an
import jieba
import re

class ZHG2P:
    @staticmethod
    def retone(p):
        p = p.replace('˧˩˧', '↓') # third tone
        p = p.replace('˧˥', '↗')  # second tone
        p = p.replace('˥˩', '↘')  # fourth tone
        p = p.replace('˥', '→')   # first tone
        p = p.replace(chr(635)+chr(809), 'ɨ').replace(chr(633)+chr(809), 'ɨ')
        assert chr(809) not in p, p
        return p

    @staticmethod
    def py2ipa(py):
        return ''.join(ZHG2P.retone(p) for p in pinyin_to_ipa(py)[0])

    @staticmethod
    def word2ipa(w):
        pinyins = lazy_pinyin(w, style=Style.TONE3, neutral_tone_with_five=True)
        return ''.join(ZHG2P.py2ipa(py) for py in pinyins)

    @staticmethod
    def preprocess(text):
        text = text.replace('、', ', ').replace('，', ', ')
        text = text.replace('。', '. ')
        text = text.replace('«', ' “').replace('»', '” ')
        text = text.replace('《', ' “').replace('》', '” ')
        text = text.replace('（', ' (').replace('）', ') ')
        text = text.replace('！', '! ')
        text = text.replace('：', ': ')
        text = text.replace('；', '; ')
        text = text.replace('？', '? ')
        return text.strip()

    def __call__(self, text, zh='\u4E00-\u9FFF'):
        if not text:
            return ''
        text = ZHG2P.preprocess(text)
        text = cn2an.transform(text, 'an2cn')
        is_zh = re.match(f'[{zh}]', text[0])
        result = ''
        for segment in re.findall(f'[{zh}]+|[^{zh}]+', text):
            # print(is_zh, segment)
            if is_zh:
                words = jieba.lcut(segment, cut_all=False)
                segment = ' '.join(ZHG2P.word2ipa(w) for w in words)
            result += segment
            is_zh = not is_zh
        return result.replace(chr(815), '')
