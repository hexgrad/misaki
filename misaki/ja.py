from .num2kana import Convert
from .token import MToken
from typing import List, Optional, Tuple
import pyopenjtalk
import re

M2P = {
chr(12449): 'a', #ァ
chr(12450): 'a', #ア
chr(12451): 'i', #ィ
chr(12452): 'i', #イ
chr(12453): 'ɯ', #ゥ
chr(12454): 'ɯ', #ウ
chr(12455): 'e', #ェ
chr(12456): 'e', #エ
chr(12457): 'o', #ォ
chr(12458): 'o', #オ
chr(12459): 'ka', #カ
chr(12460): 'ɡa', #ガ
chr(12461): 'ki', #キ
chr(12462): 'ɡi', #ギ
chr(12463): 'kɯ', #ク
chr(12464): 'ɡɯ', #グ
chr(12465): 'ke', #ケ
chr(12466): 'ɡe', #ゲ
chr(12467): 'ko', #コ
chr(12468): 'ɡo', #ゴ
chr(12469): 'sa', #サ
chr(12470): 'za', #ザ
chr(12471): 'ɕi', #シ
chr(12472): 'ʥi', #ジ
chr(12473): 'sɨ', #ス
chr(12474): 'zɨ', #ズ
chr(12475): 'se', #セ
chr(12476): 'ze', #ゼ
chr(12477): 'so', #ソ
chr(12478): 'zo', #ゾ
chr(12479): 'ta', #タ
chr(12480): 'da', #ダ
chr(12481): 'ʨi', #チ
chr(12482): 'ʥi', #ヂ
# chr(12483): '#', #ッ
chr(12484): 'ʦɨ', #ツ
chr(12485): 'ʥɨ', #ヅ
chr(12486): 'te', #テ
chr(12487): 'de', #デ
chr(12488): 'to', #ト
chr(12489): 'do', #ド
chr(12490): 'na', #ナ
chr(12491): 'ɲi', #ニ
chr(12492): 'nɯ', #ヌ
chr(12493): 'ne', #ネ
chr(12494): 'no', #ノ
chr(12495): 'ha', #ハ
chr(12496): 'ba', #バ
chr(12497): 'pa', #パ
chr(12498): 'çi', #ヒ
chr(12499): 'bi', #ビ
chr(12500): 'pi', #ピ
chr(12501): 'ɸɯ', #フ
chr(12502): 'bɯ', #ブ
chr(12503): 'pɯ', #プ
chr(12504): 'he', #ヘ
chr(12505): 'be', #ベ
chr(12506): 'pe', #ペ
chr(12507): 'ho', #ホ
chr(12508): 'bo', #ボ
chr(12509): 'po', #ポ
chr(12510): 'ma', #マ
chr(12511): 'mi', #ミ
chr(12512): 'mɯ', #ム
chr(12513): 'me', #メ
chr(12514): 'mo', #モ
chr(12515): 'ja', #ャ
chr(12516): 'ja', #ヤ
chr(12517): 'jɯ', #ュ
chr(12518): 'jɯ', #ユ
chr(12519): 'jo', #ョ
chr(12520): 'jo', #ヨ
chr(12521): 'ɽa', #ラ
chr(12522): 'ɽi', #リ
chr(12523): 'ɽɯ', #ル
chr(12524): 'ɽe', #レ
chr(12525): 'ɽo', #ロ
chr(12526): 'βa', #ヮ
chr(12527): 'βa', #ワ
chr(12528): 'i', #ヰ
chr(12529): 'e', #ヱ
chr(12530): 'o', #ヲ
# chr(12531): 'ɴ', #ン
chr(12532): 'vɯ', #ヴ
chr(12533): 'ka', #ヵ
chr(12534): 'ke', #ヶ
chr(12535): 'va', #ヷ
chr(12536): 'vi', #ヸ
chr(12537): 've', #ヹ
chr(12538): 'vo', #ヺ
}
for o in range(12449, 12449+90):
    assert o in (12483, 12531) or chr(o) in M2P, (o, chr(o))
assert len(M2P) == 88, len(M2P)

M2P.update({
chr(12452)+chr(12455): 'je', #イェ
chr(12454)+chr(12449): 'βa', #ウァ
chr(12454)+chr(12451): 'βi', #ウィ
chr(12454)+chr(12455): 'βe', #ウェ
chr(12454)+chr(12457): 'βo', #ウォ
chr(12461)+chr(12455): 'kʲe', #キェ
chr(12461)+chr(12515): 'kʲa', #キャ
chr(12461)+chr(12517): 'kʲɨ', #キュ
chr(12461)+chr(12519): 'kʲo', #キョ
chr(12462)+chr(12455): 'ɡʲe', #ギェ
chr(12462)+chr(12515): 'ɡʲa', #ギャ
chr(12462)+chr(12517): 'ɡʲɨ', #ギュ
chr(12462)+chr(12519): 'ɡʲo', #ギョ
chr(12463)+chr(12449): 'kᵝa', #クァ
chr(12463)+chr(12451): 'kᵝi', #クィ
chr(12463)+chr(12455): 'kᵝe', #クェ
chr(12463)+chr(12457): 'kᵝo', #クォ
chr(12463)+chr(12526): 'kᵝa', #クヮ
chr(12464)+chr(12449): 'ɡᵝa', #グァ
chr(12464)+chr(12451): 'ɡᵝi', #グィ
chr(12464)+chr(12455): 'ɡᵝe', #グェ
chr(12464)+chr(12457): 'ɡᵝo', #グォ
chr(12464)+chr(12526): 'ɡᵝa', #グヮ
chr(12471)+chr(12455): 'ɕe', #シェ
chr(12471)+chr(12515): 'ɕa', #シャ
chr(12471)+chr(12517): 'ɕɨ', #シュ
chr(12471)+chr(12519): 'ɕo', #ショ
chr(12472)+chr(12455): 'ʥe', #ジェ
chr(12472)+chr(12515): 'ʥa', #ジャ
chr(12472)+chr(12517): 'ʥɨ', #ジュ
chr(12472)+chr(12519): 'ʥo', #ジョ
chr(12473)+chr(12451): 'si', #スィ
chr(12474)+chr(12451): 'zi', #ズィ
chr(12481)+chr(12455): 'ʨe', #チェ
chr(12481)+chr(12515): 'ʨa', #チャ
chr(12481)+chr(12517): 'ʨɨ', #チュ
chr(12481)+chr(12519): 'ʨo', #チョ
chr(12482)+chr(12455): 'ʥe', #ヂェ
chr(12482)+chr(12515): 'ʥa', #ヂャ
chr(12482)+chr(12517): 'ʥɨ', #ヂュ
chr(12482)+chr(12519): 'ʥo', #ヂョ
chr(12484)+chr(12449): 'ʦa', #ツァ
chr(12484)+chr(12451): 'ʦi', #ツィ
chr(12484)+chr(12455): 'ʦe', #ツェ
chr(12484)+chr(12457): 'ʦo', #ツォ
chr(12486)+chr(12451): 'ti', #ティ
chr(12486)+chr(12517): 'tʲɨ', #テュ
chr(12487)+chr(12451): 'di', #ディ
chr(12487)+chr(12517): 'dʲɨ', #デュ
chr(12488)+chr(12453): 'tɯ', #トゥ
chr(12489)+chr(12453): 'dɯ', #ドゥ
chr(12491)+chr(12455): 'ɲe', #ニェ
chr(12491)+chr(12515): 'ɲa', #ニャ
chr(12491)+chr(12517): 'ɲɨ', #ニュ
chr(12491)+chr(12519): 'ɲo', #ニョ
chr(12498)+chr(12455): 'çe', #ヒェ
chr(12498)+chr(12515): 'ça', #ヒャ
chr(12498)+chr(12517): 'çɨ', #ヒュ
chr(12498)+chr(12519): 'ço', #ヒョ
chr(12499)+chr(12455): 'bʲe', #ビェ
chr(12499)+chr(12515): 'bʲa', #ビャ
chr(12499)+chr(12517): 'bʲɨ', #ビュ
chr(12499)+chr(12519): 'bʲo', #ビョ
chr(12500)+chr(12455): 'pʲe', #ピェ
chr(12500)+chr(12515): 'pʲa', #ピャ
chr(12500)+chr(12517): 'pʲɨ', #ピュ
chr(12500)+chr(12519): 'pʲo', #ピョ
chr(12501)+chr(12449): 'ɸa', #ファ
chr(12501)+chr(12451): 'ɸi', #フィ
chr(12501)+chr(12455): 'ɸe', #フェ
chr(12501)+chr(12457): 'ɸo', #フォ
chr(12501)+chr(12515): 'ɸʲa', #フャ
chr(12501)+chr(12517): 'ɸʲɨ', #フュ
chr(12501)+chr(12519): 'ɸʲo', #フョ
chr(12511)+chr(12455): 'mʲe', #ミェ
chr(12511)+chr(12515): 'mʲa', #ミャ
chr(12511)+chr(12517): 'mʲɨ', #ミュ
chr(12511)+chr(12519): 'mʲo', #ミョ
chr(12522)+chr(12455): 'ɽʲe', #リェ
chr(12522)+chr(12515): 'ɽʲa', #リャ
chr(12522)+chr(12517): 'ɽʲɨ', #リュ
chr(12522)+chr(12519): 'ɽʲo', #リョ
chr(12532)+chr(12449): 'va', #ヴァ
chr(12532)+chr(12451): 'vi', #ヴィ
chr(12532)+chr(12455): 've', #ヴェ
chr(12532)+chr(12457): 'vo', #ヴォ
chr(12532)+chr(12515): 'vʲa', #ヴャ
chr(12532)+chr(12517): 'vʲɨ', #ヴュ
chr(12532)+chr(12519): 'vʲo', #ヴョ
})
assert len(M2P) == 177, len(M2P)

for k in M2P:
    assert len(k) in (1, 2), k
    if len(k) == 2:
        a, b = k
        assert a in M2P and b in M2P, (a, b)

# TODO
M2P['ッ'] = 'ʔ'
M2P['ン'] = 'ɴ'
# M2P['ー'] = 'ː'
assert len(M2P) == 179, len(M2P)

TAILS = frozenset([*[v[-1] for v in M2P.values()], ']'])
assert len(TAILS) == 9, len(TAILS)

# VOWELS = frozenset('aeioɨɯ')
# assert len(VOWELS) == 6 and all(v in TAILS for v in VOWELS), len(VOWELS)

PUNCT_MAP = {'«':'“','»':'”','、':',','。':'.','《':'“','》':'”','「':'“','」':'”','【':'“','】':'”','！':'!','（':'(','）':')','：':':','；':';','？':'?'}
assert all(len(k) == len(v) == 1 for k, v in PUNCT_MAP.items())

PUNCT_VALUES = frozenset('!"(),.:;?—“”…')
assert len(PUNCT_VALUES) == 13, len(PUNCT_VALUES)

PUNCT_STARTS = frozenset('(“')
assert len(PUNCT_STARTS) == 2, len(PUNCT_STARTS)

PUNCT_STOPS = frozenset('!),.:;?”')
assert len(PUNCT_STOPS) == 8, len(PUNCT_STOPS)

class JAG2P:
    SMALL_COMBO_KANA = frozenset(['ァ', 'ィ', 'ゥ', 'ェ', 'ォ', 'ャ', 'ュ', 'ョ'])

    def __init__(self, version=None, unk='❓'):
        self.version = version
        self.unk = unk
        self.cutlet = None
        if version != '2.0':
            from .cutlet import Cutlet
            self.cutlet = Cutlet()

    @staticmethod
    def pron2moras(pron: str) -> List[str]:
        moras = []
        for k in pron:
            if k != 'ー' and k not in M2P:
                continue
            if moras and k in JAG2P.SMALL_COMBO_KANA and moras[-1][-1] != k:
                moras[-1] += k
            else:
                moras.append(k)
        return moras

    @staticmethod
    def mora2phones(m: str, last_p: str, future: Optional[str]) -> str:
        if m == 'ー':
            return last_p
        if m != 'ン':
            return M2P[m]
        # https://en.wikipedia.org/wiki/N_(kana)
        if future:
            future = M2P[future][0]
            if future in 'mpb':
                return 'm' # m before m,p,b
            elif future in 'kɡ':
                return 'ŋ' # ŋ before k,ɡ
            elif future in 'ɲʨʥ':
                return 'ɲ' # ɲ before ɲ,ʨ,ʥ
            elif future in 'ntdɽz':
                return 'n' # n before n,t,d,ɽ,z
        return 'ɴ' # ɴ otherwise

    def __call__(self, text) -> Tuple[str, Optional[List[MToken]]]:
        if self.cutlet:
            return self.cutlet(text)
        tokens = []
        last_a, last_p = 0, ''
        acc, mcount = None, 0
        for word in pyopenjtalk.run_frontend(text):
            pron, mora_size = word['pron'], word['mora_size']
            chain_flag = word['chain_flag'] == 1 and mora_size > 0 and tokens and tokens[-1]._.mora_size > 0
            if not chain_flag:
                acc, mcount = None, 0
            moras = []
            if mora_size > 0:
                moras = JAG2P.pron2moras(pron)
                assert len(moras) == mora_size, (moras, mora_size)
            acc = word['acc'] if acc is None else acc
            accents = []
            for _ in moras:
                mcount += 1
                if acc == 0:
                    accents.append(0 if mcount == 1 else (1 if last_a == 0 else 2))
                elif acc == mcount:
                    accents.append(3)
                elif 1 < mcount < acc:
                    accents.append(1 if last_a == 0 else 2)
                else:
                    accents.append(0)
                last_a = accents[-1]
            assert len(moras) == len(accents)
            surface = word['string']
            if surface in PUNCT_MAP:
                surface = PUNCT_MAP[surface]
            whitespace, phonemes = '', None
            if moras:
                phonemes = ''
                for i, (m, a) in enumerate(zip(moras, accents)):
                    ps = JAG2P.mora2phones(m, last_p=last_p, future=moras[i+1] if i < len(moras)-1 else None)
                    if a in (0, 2):# or all(v not in ps for v in VOWELS):
                        phonemes += ps
                    elif a == 1:
                        phonemes += '[' + ps
                    # elif a == 2:
                    #     phonemes += ps[:-1] + 'ˈ' + ps[-1]
                    else:
                        assert a == 3, a
                        phonemes += ps + ']'
                    last_p = ps[-1:]
            elif surface and all(s in PUNCT_VALUES for s in surface):
                phonemes = surface
                if surface[-1] in PUNCT_STOPS:
                    whitespace = ' '
                    if tokens:
                        tokens[-1].whitespace = ''
                elif surface[-1] in PUNCT_STARTS and tokens and not tokens[-1].whitespace:
                    tokens[-1].whitespace = ' '
            tokens.append(MToken(
                text=surface, tag=word['pos'],
                whitespace=whitespace, phonemes=phonemes,
                _=MToken.Underscore(
                    pron=pron, acc=word['acc'], mora_size=mora_size,
                    chain_flag=chain_flag, moras=moras, accents=accents
                )
            ))
        result = ''
        for tk in tokens:
            if tk.phonemes is None:
                result += self.unk + tk.whitespace
                continue
            if tk._.mora_size and not tk._.chain_flag and result and result[-1] in TAILS and not tk._.moras[0] == 'ン':
                result += ' '
            result += tk.phonemes + tk.whitespace
        if tokens and tokens[-1].whitespace and result.endswith(tokens[-1].whitespace):
            result = result[:-len(tokens[-1].whitespace)]
        return result, tokens
