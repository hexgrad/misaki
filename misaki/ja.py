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
chr(12453): 'u', #ゥ
chr(12454): 'u', #ウ
chr(12455): 'e', #ェ
chr(12456): 'e', #エ
chr(12457): 'o', #ォ
chr(12458): 'o', #オ
chr(12459): 'ka', #カ
chr(12460): 'ga', #ガ
chr(12461): 'ki', #キ
chr(12462): 'gi', #ギ
chr(12463): 'ku', #ク
chr(12464): 'gu', #グ
chr(12465): 'ke', #ケ
chr(12466): 'ge', #ゲ
chr(12467): 'ko', #コ
chr(12468): 'go', #ゴ
chr(12469): 'sa', #サ
chr(12470): 'za', #ザ
chr(12471): 'ɕi', #シ
chr(12472): 'ʥi', #ジ
chr(12473): 'su', #ス
chr(12474): 'zu', #ズ
chr(12475): 'se', #セ
chr(12476): 'ze', #ゼ
chr(12477): 'so', #ソ
chr(12478): 'zo', #ゾ
chr(12479): 'ta', #タ
chr(12480): 'da', #ダ
chr(12481): 'ʨi', #チ
chr(12482): 'ʥi', #ヂ
# chr(12483): '#', #ッ
chr(12484): 'ʦu', #ツ
chr(12485): 'zu', #ヅ
chr(12486): 'te', #テ
chr(12487): 'de', #デ
chr(12488): 'to', #ト
chr(12489): 'do', #ド
chr(12490): 'na', #ナ
chr(12491): 'ni', #ニ
chr(12492): 'nu', #ヌ
chr(12493): 'ne', #ネ
chr(12494): 'no', #ノ
chr(12495): 'ha', #ハ
chr(12496): 'ba', #バ
chr(12497): 'pa', #パ
chr(12498): 'hi', #ヒ
chr(12499): 'bi', #ビ
chr(12500): 'pi', #ピ
chr(12501): 'fu', #フ
chr(12502): 'bu', #ブ
chr(12503): 'pu', #プ
chr(12504): 'he', #ヘ
chr(12505): 'be', #ベ
chr(12506): 'pe', #ペ
chr(12507): 'ho', #ホ
chr(12508): 'bo', #ボ
chr(12509): 'po', #ポ
chr(12510): 'ma', #マ
chr(12511): 'mi', #ミ
chr(12512): 'mu', #ム
chr(12513): 'me', #メ
chr(12514): 'mo', #モ
chr(12515): 'ja', #ャ
chr(12516): 'ja', #ヤ
chr(12517): 'ju', #ュ
chr(12518): 'ju', #ユ
chr(12519): 'jo', #ョ
chr(12520): 'jo', #ヨ
chr(12521): 'ra', #ラ
chr(12522): 'ri', #リ
chr(12523): 'ru', #ル
chr(12524): 're', #レ
chr(12525): 'ro', #ロ
chr(12526): 'wa', #ヮ
chr(12527): 'wa', #ワ
chr(12528): 'i', #ヰ
chr(12529): 'e', #ヱ
chr(12530): 'o', #ヲ
# chr(12531): 'ɴ', #ン
chr(12532): 'vu', #ヴ
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
chr(12454)+chr(12451): 'wi', #ウィ
chr(12454)+chr(12453): 'wu', #ウゥ
chr(12454)+chr(12455): 'we', #ウェ
chr(12454)+chr(12457): 'wo', #ウォ
chr(12461)+chr(12451): 'ᶄi', #キィ
chr(12461)+chr(12455): 'ᶄe', #キェ
chr(12461)+chr(12515): 'ᶄa', #キャ
chr(12461)+chr(12517): 'ᶄu', #キュ
chr(12461)+chr(12519): 'ᶄo', #キョ
chr(12462)+chr(12451): 'ᶃi', #ギィ
chr(12462)+chr(12455): 'ᶃe', #ギェ
chr(12462)+chr(12515): 'ᶃa', #ギャ
chr(12462)+chr(12517): 'ᶃu', #ギュ
chr(12462)+chr(12519): 'ᶃo', #ギョ
chr(12463)+chr(12449): 'Ka', #クァ
chr(12463)+chr(12451): 'Ki', #クィ
chr(12463)+chr(12453): 'Ku', #クゥ
chr(12463)+chr(12455): 'Ke', #クェ
chr(12463)+chr(12457): 'Ko', #クォ
chr(12463)+chr(12526): 'Ka', #クヮ
chr(12464)+chr(12449): 'Ga', #グァ
chr(12464)+chr(12451): 'Gi', #グィ
chr(12464)+chr(12453): 'Gu', #グゥ
chr(12464)+chr(12455): 'Ge', #グェ
chr(12464)+chr(12457): 'Go', #グォ
chr(12464)+chr(12526): 'Ga', #グヮ
chr(12471)+chr(12455): 'ɕe', #シェ
chr(12471)+chr(12515): 'ɕa', #シャ
chr(12471)+chr(12517): 'ɕu', #シュ
chr(12471)+chr(12519): 'ɕo', #ショ
chr(12472)+chr(12455): 'ʥe', #ジェ
chr(12472)+chr(12515): 'ʥa', #ジャ
chr(12472)+chr(12517): 'ʥu', #ジュ
chr(12472)+chr(12519): 'ʥo', #ジョ
chr(12473)+chr(12451): 'si', #スィ
chr(12474)+chr(12451): 'zi', #ズィ
chr(12481)+chr(12455): 'ʨe', #チェ
chr(12481)+chr(12515): 'ʨa', #チャ
chr(12481)+chr(12517): 'ʨu', #チュ
chr(12481)+chr(12519): 'ʨo', #チョ
chr(12482)+chr(12455): 'ʥe', #ヂェ
chr(12482)+chr(12515): 'ʥa', #ヂャ
chr(12482)+chr(12517): 'ʥu', #ヂュ
chr(12482)+chr(12519): 'ʥo', #ヂョ
chr(12484)+chr(12449): 'ʦa', #ツァ
chr(12484)+chr(12451): 'ʦi', #ツィ
chr(12484)+chr(12455): 'ʦe', #ツェ
chr(12484)+chr(12457): 'ʦo', #ツォ
chr(12486)+chr(12451): 'ti', #ティ
chr(12486)+chr(12455): 'ƫe', #テェ
chr(12486)+chr(12515): 'ƫa', #テャ
chr(12486)+chr(12517): 'ƫu', #テュ
chr(12486)+chr(12519): 'ƫo', #テョ
chr(12487)+chr(12451): 'di', #ディ
chr(12487)+chr(12455): 'ᶁe', #デェ
chr(12487)+chr(12515): 'ᶁa', #デャ
chr(12487)+chr(12517): 'ᶁu', #デュ
chr(12487)+chr(12519): 'ᶁo', #デョ
chr(12488)+chr(12453): 'tu', #トゥ
chr(12489)+chr(12453): 'du', #ドゥ
chr(12491)+chr(12451): 'ɲi', #ニィ
chr(12491)+chr(12455): 'ɲe', #ニェ
chr(12491)+chr(12515): 'ɲa', #ニャ
chr(12491)+chr(12517): 'ɲu', #ニュ
chr(12491)+chr(12519): 'ɲo', #ニョ
chr(12498)+chr(12451): 'çi', #ヒィ
chr(12498)+chr(12455): 'çe', #ヒェ
chr(12498)+chr(12515): 'ça', #ヒャ
chr(12498)+chr(12517): 'çu', #ヒュ
chr(12498)+chr(12519): 'ço', #ヒョ
chr(12499)+chr(12451): 'ᶀi', #ビィ
chr(12499)+chr(12455): 'ᶀe', #ビェ
chr(12499)+chr(12515): 'ᶀa', #ビャ
chr(12499)+chr(12517): 'ᶀu', #ビュ
chr(12499)+chr(12519): 'ᶀo', #ビョ
chr(12500)+chr(12451): 'ᶈi', #ピィ
chr(12500)+chr(12455): 'ᶈe', #ピェ
chr(12500)+chr(12515): 'ᶈa', #ピャ
chr(12500)+chr(12517): 'ᶈu', #ピュ
chr(12500)+chr(12519): 'ᶈo', #ピョ
chr(12501)+chr(12449): 'fa', #ファ
chr(12501)+chr(12451): 'fi', #フィ
chr(12501)+chr(12455): 'fe', #フェ
chr(12501)+chr(12457): 'fo', #フォ
chr(12511)+chr(12451): 'ᶆi', #ミィ
chr(12511)+chr(12455): 'ᶆe', #ミェ
chr(12511)+chr(12515): 'ᶆa', #ミャ
chr(12511)+chr(12517): 'ᶆu', #ミュ
chr(12511)+chr(12519): 'ᶆo', #ミョ
chr(12522)+chr(12451): 'ᶉi', #リィ
chr(12522)+chr(12455): 'ᶉe', #リェ
chr(12522)+chr(12515): 'ᶉa', #リャ
chr(12522)+chr(12517): 'ᶉu', #リュ
chr(12522)+chr(12519): 'ᶉo', #リョ
chr(12532)+chr(12449): 'va', #ヴァ
chr(12532)+chr(12451): 'vi', #ヴィ
chr(12532)+chr(12455): 've', #ヴェ
chr(12532)+chr(12457): 'vo', #ヴォ
chr(12532)+chr(12515): 'ᶀa', #ヴャ
chr(12532)+chr(12517): 'ᶀu', #ヴュ
chr(12532)+chr(12519): 'ᶀo', #ヴョ
})
assert len(M2P) == 190, len(M2P)

P2R = [('G','gw'),('j','y'),('K','kw'),('ç','hy'),('ƫ','ty'),('ɕ','sh'),('ɲ','ny'),('ʥ','j'),('ʦ','ts'),('ʨ','ch'),('ᶀ','by'),('ᶁ','dy'),('ᶃ','gy'),('ᶄ','ky'),('ᶆ','my'),('ᶈ','py'),('ᶉ','ry')]

VOWELS = frozenset('aeiou')
assert len(VOWELS) == 5, len(VOWELS)

CONSONANTS = frozenset('bdfgGhjkKmnprstvwzçƫɕɲʥʦʨᶀᶁᶃᶄᶆᶈᶉ')
assert len(CONSONANTS) == 32, len(CONSONANTS)

for k, v in M2P.items():
    assert len(k) in (1, 2), k
    assert len(v) in (1, 2) and v[-1] in VOWELS, v
    if len(k) == 2:
        a, b = k
        assert a in M2P and b in M2P, (a, b)
    if len(v) == 2:
        assert v[0] in CONSONANTS, v
    for old, new in P2R:
        v = v.replace(old, new)

# TODO
M2P['ッ'] = 'ʔ'
M2P['ン'] = 'ɴ'
M2P['ー'] = 'ː'
assert len(M2P) == 193, len(M2P)

# TAILS = frozenset([*[v[-1] for v in M2P.values()], '↓'])
TAILS = frozenset([v[-1] for v in M2P.values()])
assert len(TAILS) == 8, len(TAILS)

PUNCT_MAP = {'«':'“','»':'”','、':',','。':'.','〈':'“','〉':'”','《':'“','》':'”','「':'“','」':'”','『':'“','』':'”','【':'“','】':'”','！':'!','（':'(','）':')','：':':','；':';','？':'?'}
assert all(len(k) == len(v) == 1 for k, v in PUNCT_MAP.items())

PUNCT_VALUES = frozenset('!"(),.:;?—“”…')
assert len(PUNCT_VALUES) == 13, len(PUNCT_VALUES)

PUNCT_STARTS = frozenset('(“')
assert len(PUNCT_STARTS) == 2, len(PUNCT_STARTS)

PUNCT_STOPS = frozenset('!),.:;?”')
assert len(PUNCT_STOPS) == 8, len(PUNCT_STOPS)

class JAG2P:
    def __init__(self, version='cutlet', unk='❓'):
        assert version in ('cutlet', 'pyopenjtalk'), version
        self.version = version
        self.unk = unk
        self.cutlet = None
        if version == 'cutlet':
            from .cutlet import Cutlet
            self.cutlet = Cutlet()

    @staticmethod
    def pron2moras(pron: str) -> List[str]:
        moras = []
        for k in pron:
            if k not in M2P: #and k != 'ー':
                continue
            if moras and moras[-1] + k in M2P:
                moras[-1] += k
            else:
                moras.append(k)
        return moras

    def __call__(self, text) -> Tuple[str, Optional[List[MToken]]]:
        if self.cutlet:
            return self.cutlet(text)
        tokens = []
        last_a, last_p = 0, ''
        acc, mcount = None, 0
        for word in pyopenjtalk.run_frontend(text):
            pron, mora_size = word['pron'], word['mora_size']
            moras = []
            if mora_size > 0:
                moras = JAG2P.pron2moras(pron)
                assert len(moras) == mora_size or len(moras) + (1 if moras[0] == 'ー' else 0) == mora_size, (moras, mora_size)
            chain_flag = mora_size > 0 and tokens and tokens[-1]._.mora_size > 0 and (word['chain_flag'] == 1 or moras[0] == 'ー')
            if not chain_flag:
                acc, mcount = None, 0
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
            whitespace, phonemes, pitch = '', None, None
            if moras:
                phonemes, pitch = '', ''
                for i, (m, a) in enumerate(zip(moras, accents)):
                    ps = M2P[m] #last_p if m == 'ー' else M2P[m]
                    phonemes += ps
                    pitch += ('_' if a == 0 else ('^' if a == 3 else '-')) * len(ps)
                    # if a in (0, 2):# or all(v not in ps for v in VOWELS):
                    #     phonemes += ps
                    # elif a == 1:
                    #     phonemes += '↑' + ps
                    # else:
                    #     assert a == 3, a
                    #     if i > 0 and accents[i-1] == 0:
                    #         phonemes += '↑'
                    #     elif i == 0 and chain_flag and tokens[-1]._.accents[-1] == 0:
                    #         phonemes += '↑'
                    #     phonemes += ps + '↓'
                    # last_p = ps[-1:]
            elif surface and all(s in PUNCT_VALUES for s in surface):
                phonemes = surface
                if surface[-1] in PUNCT_STOPS:
                    whitespace = ' '
                    if tokens:
                        tokens[-1].whitespace = ''
                elif surface[-1] in PUNCT_STARTS and tokens and not tokens[-1].whitespace:
                    tokens[-1].whitespace = ' '
            if tokens and phonemes is None and surface == '・' or surface and not surface.strip():
                tokens[-1].whitespace = ' '
                continue
            tokens.append(MToken(
                text=surface, tag=word['pos'],
                whitespace=whitespace, phonemes=phonemes,
                _=MToken.Underscore(
                    pron=pron, acc=word['acc'], mora_size=mora_size,
                    chain_flag=chain_flag, moras=moras, accents=accents, pitch=pitch
                )
            ))
        result, pitch = '', ''
        for tk in tokens:
            if tk.phonemes is None:
                result += self.unk + tk.whitespace
                pitch += 'j' * len(self.unk + tk.whitespace)
                continue
            if tk._.mora_size and not tk._.chain_flag and result and result[-1] in TAILS and not tk._.moras[0] == 'ン':
                result += ' '
                pitch += 'j'
            result += tk.phonemes + tk.whitespace
            pitch += (('j' * len(tk.phonemes)) if tk._.pitch is None else tk._.pitch) + 'j' * len(tk.whitespace)
        if tokens and tokens[-1].whitespace and result.endswith(tokens[-1].whitespace):
            result = result[:-len(tokens[-1].whitespace)]
            pitch = pitch[:len(result)]
        return result + pitch, tokens
