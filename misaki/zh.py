from .transcription import pinyin_to_ipa
from pypinyin import lazy_pinyin, Style
from typing import Tuple
import cn2an
import jieba
import re

class ZHG2P:
    def __init__(self, version=None, unk='❓', en_callable=None):
        self.version = version
        self.frontend = None
        self.en_callable = en_callable
        if version == '1.1':
            from .zh_frontend import ZHFrontend
            self.frontend = ZHFrontend(unk=unk)
            if en_callable is None:
                print('Warning: en_callable is None, so English may be removed')

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
    def map_punctuation(text):
        text = text.replace('、', ', ').replace('，', ', ')
        text = text.replace('。', '. ').replace('．', '. ')
        text = text.replace('！', '! ')
        text = text.replace('：', ': ')
        text = text.replace('；', '; ')
        text = text.replace('？', '? ')
        text = text.replace('«', ' “').replace('»', '” ')
        text = text.replace('《', ' “').replace('》', '” ')
        text = text.replace('「', ' “').replace('」', '” ')
        text = text.replace('【', ' “').replace('】', '” ')
        text = text.replace('（', ' (').replace('）', ') ')
        return text.strip()

    @staticmethod
    def legacy_call(text) -> str:
        is_zh = re.match(f'[\u4E00-\u9FFF]', text[0])
        result = ''
        for segment in re.findall(f'[\u4E00-\u9FFF]+|[^\u4E00-\u9FFF]+', text):
            if is_zh:
                words = jieba.lcut(segment, cut_all=False)
                segment = ' '.join(ZHG2P.word2ipa(w) for w in words)
            result += segment
            is_zh = not is_zh
        return result.replace(chr(815), '')

    def __call__(self, text, en_callable=None) -> Tuple[str, None]:
        if not text.strip():
            return '', None
        text = cn2an.transform(text, 'an2cn')
        text = ZHG2P.map_punctuation(text)
        if self.frontend is None:
            return ZHG2P.legacy_call(text), None
        # TODO: Interleaved English is brittle, needs improvement.
        en_callable = self.en_callable if en_callable is None else en_callable
        segments = []
        for en, zh in re.findall(r'([A-Za-z \'-]*[A-Za-z][A-Za-z \'-]*)|([^A-Za-z]+)', text):
            en, zh = en.strip(), zh.strip()
            if zh:
                segments.append(self.frontend(zh)[0])
            elif en_callable is None:
                segments.append(self.unk)
            else:
                segments.append(en_callable(en))
        # TODO: Return List[MToken] instead of None
        return ' '.join(segments), None
