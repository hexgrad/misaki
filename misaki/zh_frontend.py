# ADAPTED from https://github.com/PaddlePaddle/PaddleSpeech/blob/develop/paddlespeech/t2s/frontend/zh_frontend.py
# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from .token import MToken
import re
from operator import itemgetter
from typing import List

import jieba.posseg as psg
from pypinyin import lazy_pinyin
from pypinyin import load_phrases_dict
from pypinyin import load_single_dict
from pypinyin import Style
from pypinyin_dict.phrase_pinyin_data import large_pinyin

from .tone_sandhi import ToneSandhi

INITIALS = [
    'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'zh', 'ch', 'sh',
    'r', 'z', 'c', 's', 'j', 'q', 'x'
]
INITIALS += ['y', 'w', ' ']#, 'spl', 'spn', 'sil']

# 0 for None, 5 for neutral
TONES = ["0", "1", "2", "3", "4", "5"]

ZH_MAP = {"b":"ㄅ","p":"ㄆ","m":"ㄇ","f":"ㄈ","d":"ㄉ","t":"ㄊ","n":"ㄋ","l":"ㄌ","g":"ㄍ","k":"ㄎ","h":"ㄏ","j":"ㄐ","q":"ㄑ","x":"ㄒ","zh":"ㄓ","ch":"ㄔ","sh":"ㄕ","r":"ㄖ","z":"ㄗ","c":"ㄘ","s":"ㄙ","a":"ㄚ","o":"ㄛ","e":"ㄜ","ie":"ㄝ","ai":"ㄞ","ei":"ㄟ","ao":"ㄠ","ou":"ㄡ","an":"ㄢ","en":"ㄣ","ang":"ㄤ","eng":"ㄥ","er":"ㄦ","i":"ㄧ","u":"ㄨ","v":"ㄩ","ii":"ㄭ","iii":"十","ve":"月","ia":"压","ian":"言","iang":"阳","iao":"要","in":"阴","ing":"应","iong":"用","iou":"又","ong":"中","ua":"穵","uai":"外","uan":"万","uang":"王","uei":"为","uen":"文","ueng":"瓮","uo":"我","van":"元","vn":"云"}
for p in ';:,.!?/—…"()“” 12345R':
    assert p not in ZH_MAP, p
    ZH_MAP[p] = p

class ZHFrontend:
    def __init__(self, unk='❓'):
        self.unk = unk
        self.punc = frozenset(';:,.!?—…"()“”')
        self.phrases_dict = {
            '开户行': [['ka1i'], ['hu4'], ['hang2']],
            '发卡行': [['fa4'], ['ka3'], ['hang2']],
            '放款行': [['fa4ng'], ['kua3n'], ['hang2']],
            '茧行': [['jia3n'], ['hang2']],
            '行号': [['hang2'], ['ha4o']],
            '各地': [['ge4'], ['di4']],
            '借还款': [['jie4'], ['hua2n'], ['kua3n']],
            '时间为': [['shi2'], ['jia1n'], ['we2i']],
            '为准': [['we2i'], ['zhu3n']],
            '色差': [['se4'], ['cha1']],
            '嗲': [['dia3']],
            '呗': [['bei5']],
            '不': [['bu4']],
            '咗': [['zuo5']],
            '嘞': [['lei5']],
            '掺和': [['chan1'], ['huo5']]
        }
        self.must_erhua = {
            "小院儿", "胡同儿", "范儿", "老汉儿", "撒欢儿", "寻老礼儿", "妥妥儿", "媳妇儿"
        }
        self.not_erhua = {
            "虐儿", "为儿", "护儿", "瞒儿", "救儿", "替儿", "有儿", "一儿", "我儿", "俺儿", "妻儿",
            "拐儿", "聋儿", "乞儿", "患儿", "幼儿", "孤儿", "婴儿", "婴幼儿", "连体儿", "脑瘫儿",
            "流浪儿", "体弱儿", "混血儿", "蜜雪儿", "舫儿", "祖儿", "美儿", "应采儿", "可儿", "侄儿",
            "孙儿", "侄孙儿", "女儿", "男儿", "红孩儿", "花儿", "虫儿", "马儿", "鸟儿", "猪儿", "猫儿",
            "狗儿", "少儿"
        }
        # tone sandhi
        self.tone_modifier = ToneSandhi()
        # g2p
        self._init_pypinyin()

    def _init_pypinyin(self):
        """
        Load pypinyin G2P module.
        """
        large_pinyin.load()
        load_phrases_dict(self.phrases_dict)
        # 调整字的拼音顺序
        load_single_dict({ord(u'地'): u'de,di4'})

    def _get_initials_finals(self, word: str) -> List[List[str]]:
        """
        Get word initial and final by pypinyin or g2pM
        """
        initials = []
        finals = []
        orig_initials = lazy_pinyin(
            word, neutral_tone_with_five=True, style=Style.INITIALS)
        orig_finals = lazy_pinyin(
            word, neutral_tone_with_five=True, style=Style.FINALS_TONE3)
        # after pypinyin==0.44.0, '嗯' need to be n2, cause the initial and final consonants cannot be empty at the same time
        en_index = [index for index, c in enumerate(word) if c == "嗯"]
        for i in en_index:
            orig_finals[i] = "n2"

        for c, v in zip(orig_initials, orig_finals):
            if re.match(r'i\d', v):
                if c in ['z', 'c', 's']:
                    # zi, ci, si
                    v = re.sub('i', 'ii', v)
                elif c in ['zh', 'ch', 'sh', 'r']:
                    # zhi, chi, shi
                    v = re.sub('i', 'iii', v)
            initials.append(c)
            finals.append(v)

        return initials, finals

    def _merge_erhua(self,
                     initials: List[str],
                     finals: List[str],
                     word: str,
                     pos: str) -> List[List[str]]:
        """
        Do erhub.
        """
        # fix er1
        for i, phn in enumerate(finals):
            if i == len(finals) - 1 and word[i] == "儿" and phn == 'er1':
                finals[i] = 'er2'

        # 发音
        if word not in self.must_erhua and (word in self.not_erhua or
                                            pos in {"a", "j", "nr"}):
            return initials, finals

        # "……" 等情况直接返回
        if len(finals) != len(word):
            return initials, finals

        assert len(finals) == len(word)

        # 不发音
        new_initials = []
        new_finals = []
        for i, phn in enumerate(finals):
            if i == len(finals) - 1 and word[i] == "儿" and phn in {
                    "er2", "er5"
            } and word[-2:] not in self.not_erhua and new_finals:
                new_finals[-1] = new_finals[-1][:-1] + "R" + new_finals[-1][-1]
            else:
                new_initials.append(initials[i])
                new_finals.append(phn)

        return new_initials, new_finals

    def __call__(self, text: str, with_erhua: bool = True) -> List[MToken]:
        """
        Return: list of list phonemes.
            [['w', 'o3', 'm', 'en2', ' '], ...]
        """
        # segments = sentences
        tokens = []

        # split by punctuation
        # for seg in segments:
            # remove all English words in the sentence
            # seg = re.sub('[a-zA-Z]+', '', seg)

        # [(word, pos), ...]
        seg_cut = psg.lcut(text)
        # fix wordseg bad case for sandhi
        seg_cut = self.tone_modifier.pre_merge_for_modify(seg_cut)

        # 为了多音词获得更好的效果，这里采用整句预测
        initials = []
        finals = []
        # pypinyin, g2pM
        for word, pos in seg_cut:
            if pos == 'x' and '\u4E00' <= min(word) and max(word) <= '\u9FFF':
                pos = 'X'
            elif pos != 'x' and word in self.punc:
                pos = 'x'
            tk = MToken(text=word, tag=pos, whitespace='')
            if pos in ('x', 'eng'):
                if not word.isspace():
                    if pos == 'x' and word in self.punc:
                        tk.phonemes = word
                    tokens.append(tk)
                elif tokens:
                    tokens[-1].whitespace += word
                continue
            elif tokens and tokens[-1].tag not in ('x', 'eng') and not tokens[-1].whitespace:
                tokens[-1].whitespace = '/'

            # g2p
            sub_initials, sub_finals = self._get_initials_finals(word)
            # tone sandhi
            sub_finals = self.tone_modifier.modified_tone(word, pos,
                                                          sub_finals)
            # er hua
            if with_erhua:
                sub_initials, sub_finals = self._merge_erhua(
                    sub_initials, sub_finals, word, pos)

            initials.append(sub_initials)
            finals.append(sub_finals)
            # assert len(sub_initials) == len(sub_finals) == len(word)

            # sum(iterable[, start])
            # initials = sum(initials, [])
            # finals = sum(finals, [])

            phones = []
            for c, v in zip(sub_initials, sub_finals):
                # NOTE: post process for pypinyin outputs
                # we discriminate i, ii and iii
                if c:
                    phones.append(c)
                # replace punctuation by ` `
                # if c and c in self.punc:
                #     phones.append(c)
                if v and (v not in self.punc or v != c):# and v not in self.rhy_phns:
                    phones.append(v)
            phones = '_'.join(phones).replace('_eR', '_er').replace('R', '_R')
            phones = re.sub(r'(?=\d)', '_', phones).split('_')
            tk.phonemes = ''.join(ZH_MAP.get(p, self.unk) for p in phones)
            tokens.append(tk)

        result = ''.join((self.unk if tk.phonemes is None else tk.phonemes) + tk.whitespace for tk in tokens)

        return result, tokens
