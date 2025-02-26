from . import data
from .token import MToken
from dataclasses import dataclass, replace
from num2words import num2words
from typing import List, Optional, Tuple, Union
import importlib.resources
import json
import numpy as np
import re
import spacy
import unicodedata

DIPHTHONGS = frozenset('AIOQWYʤʧ')
def stress_weight(ps):
    return sum(2 if c in DIPHTHONGS else 1 for c in ps) if ps else 0

@dataclass
class TokenContext:
    future_vowel: Optional[bool] = None
    future_to: bool = False

# BEGIN HACK: Scope so we don't use regex elsewhere.
def make_subtokenize_once():
    import regex
    SUBTOKEN_REGEX = regex.compile(r"^['‘’]+|\p{Lu}(?=\p{Lu}\p{Ll})|(?:^-)?(?:\d?[,.]?\d)+|[-_]+|['‘’]{2,}|\p{L}*?(?:['‘’]\p{L})*?\p{Ll}(?=\p{Lu})|\p{L}+(?:['‘’]\p{L})*|[^-_\p{L}'‘’\d]|['‘’]+$")
    return (lambda word: regex.findall(SUBTOKEN_REGEX, word))
subtokenize = make_subtokenize_once()
del make_subtokenize_once
# END HACK: Delete make_subtokenize_once so we can't call it again.

LINK_REGEX = re.compile(r'\[([^\]]+)\]\(([^\)]*)\)')

SUBTOKEN_JUNKS = frozenset("',-._‘’/")
PUNCTS = frozenset(';:,.!?—…"“”')
NON_QUOTE_PUNCTS = frozenset(p for p in PUNCTS if p not in '"“”')

# https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
PUNCT_TAGS = frozenset([".",",","-LRB-","-RRB-","``",'""',"''",":","$","#",'NFP'])
PUNCT_TAG_PHONEMES = {'-LRB-':'(', '-RRB-':')', '``':chr(8220), '""':chr(8221), "''":chr(8221)}

LEXICON_ORDS = [39, 45, *range(65, 91), *range(97, 123)]
CONSONANTS = frozenset('bdfhjklmnpstvwzðŋɡɹɾʃʒʤʧθ')
# EXTENDER = 'ː'
US_TAUS = frozenset('AIOWYiuæɑəɛɪɹʊʌ')

CURRENCIES = {
    '$': ('dollar', 'cent'),
    '£': ('pound', 'pence'),
    '€': ('euro', 'cent'),
}
ORDINALS = frozenset(['st', 'nd', 'rd', 'th'])

ADD_SYMBOLS = {'.':'dot', '/':'slash'}
SYMBOLS = {'%':'percent', '&':'and', '+':'plus', '@':'at'}

US_VOCAB = frozenset('AIOWYbdfhijklmnpstuvwzæðŋɑɔəɛɜɡɪɹɾʃʊʌʒʤʧˈˌθᵊᵻ') # ɐ
GB_VOCAB = frozenset('AIQWYabdfhijklmnpstuvwzðŋɑɒɔəɛɜɡɪɹʃʊʌʒʤʧˈˌːθᵊ') # ɐ

STRESSES = 'ˌˈ'
PRIMARY_STRESS = STRESSES[1]
SECONDARY_STRESS = STRESSES[0]
VOWELS = frozenset('AIOQWYaiuæɑɒɔəɛɜɪʊʌᵻ')
def apply_stress(ps, stress):
    def restress(ps):
        ips = list(enumerate(ps))
        stresses = {i: next(j for j, v in ips[i:] if v in VOWELS) for i, p in ips if p in STRESSES}
        for i, j in stresses.items():
            _, s = ips[i]
            ips[i] = (j - 0.5, s)
        ps = ''.join([p for _, p in sorted(ips)])
        return ps
    if stress is None:
        return ps
    elif stress < -1:
        return ps.replace(PRIMARY_STRESS, '').replace(SECONDARY_STRESS, '')
    elif stress == -1 or (stress in (0, -0.5) and PRIMARY_STRESS in ps):
        return ps.replace(SECONDARY_STRESS, '').replace(PRIMARY_STRESS, SECONDARY_STRESS)
    elif stress in (0, 0.5, 1) and all(s not in ps for s in STRESSES):
        if all(v not in ps for v in VOWELS):
            return ps
        return restress(SECONDARY_STRESS + ps)
    elif stress >= 1 and PRIMARY_STRESS not in ps and SECONDARY_STRESS in ps:
        return ps.replace(SECONDARY_STRESS, PRIMARY_STRESS)
    elif stress > 1 and all(s not in ps for s in STRESSES):
        if all(v not in ps for v in VOWELS):
            return ps
        return restress(PRIMARY_STRESS + ps)
    return ps

class Lexicon:
    @staticmethod
    def grow_dictionary(d):
        # HACK: Inefficient but correct.
        e = {}
        for k, v in d.items():
            if len(k) < 2:
                continue
            if k == k.lower():
                if k != k.capitalize():
                    e[k.capitalize()] = v
            elif k == k.lower().capitalize():
                e[k.lower()] = v
        return {**e, **d}

    def __init__(self, british):
        self.british = british
        self.cap_stresses = (0.5, 2)
        self.golds = {}
        self.silvers = {}
        with importlib.resources.open_text(data, f"{'gb' if british else 'us'}_gold.json") as r:
            self.golds = Lexicon.grow_dictionary(json.load(r))
        with importlib.resources.open_text(data, f"{'gb' if british else 'us'}_silver.json") as r:
            self.silvers = Lexicon.grow_dictionary(json.load(r))
        assert all(isinstance(v, str) or isinstance(v, dict) for v in self.golds.values())
        vocab = GB_VOCAB if british else US_VOCAB
        for vs in self.golds.values():
            if isinstance(vs, str):
                assert all(c in vocab for c in vs), vs
            else:
                assert 'DEFAULT' in vs, vs
                for v in vs.values():
                    assert v is None or all(c in vocab for c in v), v

    def get_NNP(self, word):
        ps = [self.golds.get(c.upper()) for c in word if c.isalpha()]
        if None in ps:
            return None, None
        ps = apply_stress(''.join(ps), 0)
        ps = ps.rsplit(SECONDARY_STRESS, 1)
        return PRIMARY_STRESS.join(ps), 3

    def get_special_case(self, word, tag, stress, ctx):
        if tag == 'ADD' and word in ADD_SYMBOLS:
            return self.lookup(ADD_SYMBOLS[word], None, -0.5, ctx)
        elif word in SYMBOLS:
            return self.lookup(SYMBOLS[word], None, None, ctx)
        elif '.' in word.strip('.') and word.replace('.', '').isalpha() and len(max(word.split('.'), key=len)) < 3:
            return self.get_NNP(word)
        elif word == 'a' or (word == 'A' and tag == 'DT'):
            return 'ɐ', 4
        elif word in ('am', 'Am', 'AM'):
            if tag.startswith('NN'):
                return self.get_NNP(word)
            elif ctx.future_vowel is None or word != 'am' or stress and stress > 0:
                return self.golds['am'], 4
            return 'ɐm', 4
        elif word in ('an', 'An', 'AN'):
            if word == 'AN' and tag.startswith('NN'):
                return self.get_NNP(word)
            return 'ɐn', 4
        elif word == 'I' and tag == 'PRP':
            return f'{SECONDARY_STRESS}I', 4
        elif word in ('by', 'By', 'BY') and Lexicon.get_parent_tag(tag) == 'ADV':
            return 'bˈI', 4
        elif word in ('to', 'To') or (word == 'TO' and tag in ('TO', 'IN')):
            return {None: self.golds['to'], False: 'tə', True: 'tʊ'}[ctx.future_vowel], 4
        elif word in ('the', 'The') or (word == 'THE' and tag == 'DT'):
            return 'ði' if ctx.future_vowel == True else 'ðə', 4
        elif tag == 'IN' and re.match(r'(?i)vs\.?$', word):
            return self.lookup('versus', None, None, ctx)
        elif word in ('used', 'Used', 'USED'):
            if tag in ('VBD', 'JJ') and ctx.future_to:
                return self.golds['used']['VBD'], 4
            return self.golds['used']['DEFAULT'], 4
        return None, None

    @staticmethod
    def get_parent_tag(tag):
        if tag is None:
            return tag
        elif tag.startswith('VB'):
            return 'VERB'
        elif tag.startswith('NN'):
            return 'NOUN'
        elif tag.startswith('ADV') or tag.startswith('RB'): #or tag == 'RP':
            return 'ADV'
        elif tag.startswith('ADJ') or tag.startswith('JJ'):
            return 'ADJ'
        return tag

    def is_known(self, word, tag):
        if word in self.golds or word in SYMBOLS or word in self.silvers:
            return True
        elif not word.isalpha() or not all(ord(c) in LEXICON_ORDS for c in word):
            return False # TODO: café
        elif len(word) == 1:
            return True
        elif word == word.upper() and word.lower() in self.golds:
            return True
        return word[1:] == word[1:].upper()

    def lookup(self, word, tag, stress, ctx):
        is_NNP = None
        if word == word.upper() and word not in self.golds:
            word = word.lower()
            is_NNP = tag == 'NNP' #Lexicon.get_parent_tag(tag) == 'NOUN'
        ps, rating = self.golds.get(word), 4
        if ps is None and not is_NNP:
            ps, rating = self.silvers.get(word), 3
        if isinstance(ps, dict):
            if ctx and ctx.future_vowel is None and 'None' in ps:
                tag = 'None'
            elif tag not in ps:
                tag = Lexicon.get_parent_tag(tag)
            ps = ps.get(tag, ps['DEFAULT'])
        if ps is None or (is_NNP and PRIMARY_STRESS not in ps):
            ps, rating = self.get_NNP(word)
            if ps is not None:
                return ps, rating
        return apply_stress(ps, stress), rating

    def _s(self, stem):
        # https://en.wiktionary.org/wiki/-s
        if not stem:
            return None
        elif stem[-1] in 'ptkfθ':
            return stem + 's'
        elif stem[-1] in 'szʃʒʧʤ':
            return stem + ('ɪ' if self.british else 'ᵻ') + 'z'
        return stem + 'z'

    def stem_s(self, word, tag, stress, ctx):
        if len(word) > 2 and word.endswith('s') and not word.endswith('ss') and self.is_known(word[:-1], tag):
            stem = word[:-1]
        elif (word.endswith("'s") or (len(word) > 4 and word.endswith('es') and not word.endswith('ies'))) and self.is_known(word[:-2], tag):
            stem = word[:-2]
        elif len(word) > 4 and word.endswith('ies') and self.is_known(word[:-3]+'y', tag):
            stem = word[:-3] + 'y'
        else:
            return None, None
        stem, rating = self.lookup(stem, tag, stress, ctx)
        return self._s(stem), rating

    def _ed(self, stem):
        # https://en.wiktionary.org/wiki/-ed
        if not stem:
            return None
        elif stem[-1] in 'pkfθʃsʧ':
            return stem + 't'
        elif stem[-1] == 'd':
            return stem + ('ɪ' if self.british else 'ᵻ') + 'd'
        elif stem[-1] != 't':
            return stem + 'd'
        elif self.british or len(stem) < 2:
            return stem + 'ɪd'
        elif stem[-2] in US_TAUS:
            return stem[:-1] + 'ɾᵻd'
        return stem + 'ᵻd'

    def stem_ed(self, word, tag, stress, ctx):
        if word.endswith('d') and not word.endswith('dd') and self.is_known(word[:-1], tag):
            stem = word[:-1]
        elif word.endswith('ed') and not word.endswith('eed') and self.is_known(word[:-2], tag):
            stem = word[:-2]
        else:
            return None, None
        stem, rating = self.lookup(stem, tag, stress, ctx)
        return self._ed(stem), rating

    def _ing(self, stem):
        # https://en.wiktionary.org/wiki/-ing
        # if self.british:
            # TODO: Fix this
            # r = 'ɹ' if stem.endswith('ring') and stem[-1] in 'əː' else ''
            # return stem + r + 'ɪŋ'
        if not stem:
            return None
        elif self.british:
            if stem[-1] in 'əː':
                return None
        elif len(stem) > 1 and stem[-1] == 't' and stem[-2] in US_TAUS:
            return stem[:-1] + 'ɾɪŋ'
        return stem + 'ɪŋ'

    def stem_ing(self, word, tag, stress, ctx):
        if word.endswith('ing') and self.is_known(word[:-3], tag):
            stem = word[:-3]
        elif word.endswith('ing') and self.is_known(word[:-3]+'e', tag):
            stem = word[:-3] + 'e'
        elif re.search(r'([bcdgklmnprstvxz])\1ing$|cking$', word) and self.is_known(word[:-4], tag):
            stem = word[:-4]
        else:
            return None, None
        stem, rating = self.lookup(stem, tag, stress, ctx)
        return self._ing(stem), rating

    def get_word(self, word, tag, stress, ctx):
        ps, rating = self.get_special_case(word, tag, stress, ctx)
        if ps is not None:
            return ps, rating
        elif self.is_known(word, tag):
            return self.lookup(word, tag, stress, ctx)
        elif word.endswith("s'") and self.is_known(word[:-2] + "'s", tag):
            return self.lookup(word[:-2] + "'s", tag, stress, ctx)
        elif word.endswith("'") and self.is_known(word[:-1], tag):
            return self.lookup(word[:-1], tag, stress, ctx)
        _s, rating = self.stem_s(word, tag, stress, ctx)
        if _s is not None:
            return _s, rating
        _ed, rating = self.stem_ed(word, tag, stress, ctx)
        if _ed is not None:
            return _ed, rating
        _ing, rating = self.stem_ing(word, tag, 0.5 if stress is None else stress, ctx)
        if _ing is not None:
            return _ing, rating
        return None, None

    @staticmethod
    def is_currency(word):
        if '.' not in word:
            return True
        elif word.count('.') > 1:
            return False
        cents = word.split('.')[1]
        return len(cents) < 3 or set(cents) == {0}

    def get_number(self, word, currency, is_head, num_flags):
        suffix = re.search(r"[a-z']+$", word)
        suffix = suffix.group() if suffix else None
        word = word[:-len(suffix)] if suffix else word
        result = []
        if word.startswith('-'):
            result.append(self.lookup('minus', None, None, None))
            word = word[1:]
        def extend_num(num, first=True, escape=False):
            splits = re.split(r'[^a-z]+', num if escape else num2words(int(num)))
            for i, w in enumerate(splits):
                if w != 'and' or '&' in num_flags:
                    if first and i == 0 and len(splits) > 1 and w == 'one' and 'a' in num_flags:
                        result.append(('ə', 4))
                    else:
                        result.append(self.lookup(w, None, -2 if w == 'point' else None, None))
                elif w == 'and' and 'n' in num_flags and result:
                    result[-1] = (result[-1][0] + 'ən', result[-1][1])
        if not is_head and '.' not in word:
            num = word.replace(',', '')
            if num[0] == '0' or len(num) > 3:
                [extend_num(n, first=False) for n in num]
            elif len(num) == 3 and not num.endswith('00'):
                extend_num(num[0])
                if num[1] == '0':
                    result.append(self.lookup('O', None, -2, None))
                    extend_num(num[2], first=False)
                else:
                    extend_num(num[1:], first=False)
            else:
                extend_num(num)
        elif word.count('.') > 1 or not is_head:
            first = True
            for num in word.replace(',', '').split('.'):
                if not num:
                    pass
                elif num[0] == '0' or (len(num) != 2 and any(n != '0' for n in num[1:])):
                    [extend_num(n, first=False) for n in num]
                else:
                    extend_num(num, first=first)
                first = False
        elif currency in CURRENCIES and Lexicon.is_currency(word):
            pairs = [(int(num) if num else 0, unit) for num, unit in zip(word.replace(',', '').split('.'), CURRENCIES[currency])]
            if len(pairs) > 1:
                if pairs[1][0] == 0:
                    pairs = pairs[:1]
                elif pairs[0][0] == 0:
                    pairs = pairs[1:]
            for i, (num, unit) in enumerate(pairs):
                if i > 0:
                    result.append(self.lookup('and', None, None, None))
                extend_num(num, first=i==0)
                result.append(self.stem_s(unit+'s', None, None, None) if abs(num) != 1 and unit != 'pence' else self.lookup(unit, None, None, None))
        else:
            if word.isdigit():
                word = num2words(int(word), to='ordinal' if suffix in ORDINALS else ('year' if not result and len(word) == 4 else 'cardinal'))
            elif '.' not in word:
                word = num2words(int(word.replace(',', '')), to='ordinal' if suffix in ORDINALS else 'cardinal')
            else:
                word = word.replace(',', '')
                if word[0] == '.':
                    word = 'point ' + ' '.join(num2words(int(n)) for n in word[1:])
                else:
                    word = num2words(float(word))
            extend_num(word, escape=True)
        if not result:
            print('❌', 'TODO:NUM', word, currency)
            return None, None
        result, rating = ' '.join(p for p, _ in result), min(r for _, r in result)
        if suffix in ('s', "'s"):
            return self._s(result), rating
        elif suffix in ('ed', "'d"):
            return self._ed(result), rating
        elif suffix == 'ing':
            return self._ing(result), rating
        return result, rating

    def append_currency(self, ps, currency):
        if not currency:
            return ps
        currency = CURRENCIES.get(currency)
        currency = self.stem_s(currency[0]+'s', None, None, None)[0] if currency else None
        return f'{ps} {currency}' if currency else ps

    @staticmethod
    def is_number(word, is_head):
        if all(not c.isdigit() for c in word):
            return False
        suffixes = ('ing', "'d", 'ed', "'s", *ORDINALS, 's')
        for s in suffixes:
            if word.endswith(s):
                word = word[:-len(s)]
                break
        return all(c.isdigit() or c in ',.' or (is_head and i == 0 and c == '-') for i, c in enumerate(word))

    def __call__(self, t, ctx):
        word = (t.text if t.alias is None else t.alias).replace(chr(8216), "'").replace(chr(8217), "'")
        word = unicodedata.normalize('NFKC', word)
        stress = None if word == word.lower() else self.cap_stresses[int(word == word.upper())]
        ps, rating = self.get_word(word, t.tag, stress, ctx)
        if ps is not None:
            return apply_stress(self.append_currency(ps, t.currency), t.stress), rating
        elif Lexicon.is_number(word, t.is_head):
            ps, rating = self.get_number(word, t.currency, t.is_head, t.num_flags)
            return apply_stress(ps, t.stress), rating
        elif not all(ord(c) in LEXICON_ORDS for c in word):
            return None, None
        if word != word.lower() and (word == word.upper() or word[1:] == word[1:].lower()):
            ps, rating = self.get_word(word.lower(), t.tag, stress, ctx)
            if ps is not None:
                return apply_stress(self.append_currency(ps, t.currency), t.stress), rating
        return None, None

class G2P:
    def __init__(self, trf=False, british=False, fallback=None, unk='❓'):
        self.british = british
        name = f"en_core_web_{'trf' if trf else 'sm'}"
        if not spacy.util.is_package(name):
            spacy.cli.download(name)
        self.nlp = spacy.load(name)
        self.lexicon = Lexicon(british)
        self.fallback = fallback if fallback else None
        self.unk = unk

    @staticmethod
    def preprocess(text):
        result = ''
        tokens = []
        features = {}
        last_end = 0
        text = text.lstrip()
        for m in LINK_REGEX.finditer(text):
            result += text[last_end:m.start()]
            tokens.extend(text[last_end:m.start()].split())
            f = m.group(2)
            if f[1 if f[:1] in ('-', '+') else 0:].isdigit():
                f = int(f)
            elif f in ('0.5', '+0.5'):
                f = 0.5
            elif f == '-0.5':
                f = -0.5
            elif len(f) > 1 and f[0] == '/' and f[-1] == '/':
                f = f[0] + f[1:].rstrip('/')
            elif len(f) > 1 and f[0] == '#' and f[-1] == '#':
                f = f[0] + f[1:].rstrip('#')
            else:
                f = None
            if f is not None:
                features[len(tokens)] = f
            result += m.group(1)
            tokens.append(m.group(1))
            last_end = m.end()
        if last_end < len(text):
            result += text[last_end:]
            tokens.extend(text[last_end:].split())
        return result, tokens, features

    def tokenize(self, text: str, tokens, features) -> List[MToken]:
        doc = self.nlp(text)
        # print(doc._.trf_data.all_outputs[0].data.shape, doc._.trf_data.all_outputs[0].lengths)
        mutable_tokens = [MToken(text=t.text, tag=t.tag_, whitespace=t.whitespace_) for t in doc]
        if not features:
            return mutable_tokens
        align = spacy.training.Alignment.from_strings(tokens, [t.text for t in mutable_tokens])
        for k, v in features.items():
            assert isinstance(v, str) or isinstance(v, int) or v in (0.5, -0.5), (k, v)
            for i, j in enumerate(np.where(align.y2x.data == k)[0]):
                if j >= len(mutable_tokens):
                    continue
                if not isinstance(v, str):
                    mutable_tokens[j].stress = v
                elif v.startswith('/'):
                    mutable_tokens[j].is_head = i == 0
                    mutable_tokens[j].phonemes = v.lstrip('/') if i == 0 else ''
                    mutable_tokens[j].rating = 5
                # elif v.startswith('['):
                #     mutable_tokens[j].alias = v.lstrip('[') if i == 0 else ''
                elif v.startswith('#'):
                    mutable_tokens[j].num_flags = v.lstrip('#')
        return mutable_tokens

    def fold_left(self, tokens: List[MToken]) -> List[MToken]:
        result = []
        for t in tokens:
            t = MToken.merge_tokens([result.pop(), t], unk=self.unk) if result and not t.is_head else t
            result.append(t)
        return result

    @staticmethod
    def retokenize(tokens: List[MToken]) -> List[Union[MToken, List[MToken]]]:
        words = []
        currency = None
        for i, token in enumerate(tokens):
            if token.alias is None and token.phonemes is None:
                ts = [replace(token, text=t, whitespace='') for t in subtokenize(token.text)]
            else:
                ts = [token]
            ts[-1].whitespace = token.whitespace
            for j, t in enumerate(ts):
                if t.alias is not None or t.phonemes is not None:
                    pass
                elif t.tag == '$' and t.text in CURRENCIES:
                    currency = t.text
                    t.phonemes = ''
                    t.rating = 4
                elif t.tag == ':' and t.text in ('-', '–'):
                    t.phonemes = '—'
                    t.rating = 3
                elif t.tag in PUNCT_TAGS:
                    t.phonemes = PUNCT_TAG_PHONEMES.get(t.tag, ''.join(c for c in t.text if c in PUNCTS))
                    t.rating = 4
                    # if not t.phonemes:
                    #     print('❌', 'TODO:PUNCT', t.text)
                elif currency is not None:
                    if t.tag != 'CD':
                        currency = None
                    elif j+1 == len(ts) and (i+1 == len(tokens) or tokens[i+1].tag != 'CD'):
                        t.currency = currency
                elif 0 < j < len(ts)-1 and t.text == '2' and (ts[j-1].text[-1]+ts[j+1].text[0]).isalpha():
                    t.alias = 'to'
                if t.alias is not None or t.phonemes is not None:
                    words.append(t)
                elif words and isinstance(words[-1], list) and not words[-1][-1].whitespace:
                    t.is_head = False
                    words[-1].append(t)
                else:
                    words.append(t if t.whitespace else [t])
        return [w[0] if isinstance(w, list) and len(w) == 1 else w for w in words]

    @staticmethod
    def token_context(ctx, ps, token):
        vowel = ctx.future_vowel
        vowel = next((None if c in NON_QUOTE_PUNCTS else (c in VOWELS) for c in ps if any(c in s for s in (VOWELS, CONSONANTS, NON_QUOTE_PUNCTS))), vowel) if ps else vowel
        return TokenContext(future_vowel=vowel, future_to=token.is_to())

    @staticmethod
    def resolve_tokens(tokens):
        text = ''.join(t.text + t.whitespace for t in tokens[:-1]) + tokens[-1].text
        prespace = ' ' in text or '/' in text or len({0 if c.isalpha() else (1 if c.isdigit() else 2) for c in text if c not in SUBTOKEN_JUNKS}) > 1
        for i, t in enumerate(tokens):
            if t.phonemes is None:
                if i == len(tokens) - 1 and t.text in NON_QUOTE_PUNCTS:
                    t.phonemes = t.text
                    t.rating = 3
                elif all(c in SUBTOKEN_JUNKS for c in t.text):
                    t.phonemes = ''
                    t.rating = 3
            elif i > 0:
                t.prespace = prespace
        if prespace:
            return
        indices = [(PRIMARY_STRESS in t.phonemes, stress_weight(t.phonemes), i) for i, t in enumerate(tokens) if t.phonemes]
        if len(indices) == 2 and len(tokens[indices[0][2]].text) == 1:
            i = indices[1][2]
            tokens[i].phonemes = apply_stress(tokens[i].phonemes, -0.5)
            return
        elif len(indices) < 2 or sum(b for b, _, _ in indices) <= (len(indices)+1) // 2:
            return
        indices = sorted(indices)[:len(indices)//2]
        for _, _, i in indices:
            tokens[i].phonemes = apply_stress(tokens[i].phonemes, -0.5)

    def __call__(self, text: str, preprocess=True) -> Tuple[str, List[MToken]]:
        preprocess = G2P.preprocess if preprocess == True else preprocess
        text, tokens, features = preprocess(text) if preprocess else (text, [], {})
        tokens = self.tokenize(text, tokens, features)
        tokens = self.fold_left(tokens)
        tokens = G2P.retokenize(tokens)
        ctx = TokenContext()
        for i, w in reversed(list(enumerate(tokens))):
            if not isinstance(w, list):
                if w.phonemes is None:
                    w.phonemes, w.rating = self.lexicon(replace(w), ctx)
                if w.phonemes is None and self.fallback is not None:
                    w.phonemes, w.rating = self.fallback(replace(w))
                ctx = G2P.token_context(ctx, w.phonemes, w)
                continue
            left, right = 0, len(w)
            should_fallback = False
            while left < right:
                if any(t.alias is not None or t.phonemes is not None for t in w[left:right]):
                    t = None
                else:
                    t = MToken.merge_tokens(w[left:right])
                ps, rating = (None, None) if t is None else self.lexicon(t, ctx)
                if ps is not None:
                    w[left].phonemes = ps
                    w[left].rating = rating
                    for x in w[left+1:right]:
                        x.phonemes = ''
                        x.rating = rating
                    ctx = G2P.token_context(ctx, ps, t)
                    right = left
                    left = 0
                elif left + 1 < right:
                    left += 1
                else:
                    right -= 1
                    t = w[right]
                    if t.phonemes is None:
                        if all(c in SUBTOKEN_JUNKS for c in t.text):
                            t.phonemes = ''
                            t.rating = 3
                        elif self.fallback is not None:
                            should_fallback = True
                            break
                    left = 0
            if should_fallback:
                t = MToken.merge_tokens(w)
                w[0].phonemes, w[0].rating = self.fallback(t)
                for j in range(1, len(w)):
                    w[j].phonemes = ''
                    w[j].rating = w[0].rating
            else:
                G2P.resolve_tokens(w)
        tokens = [MToken.merge_tokens(t, unk=self.unk) if isinstance(t, list) else t for t in tokens]
        result = ''.join((self.unk if t.phonemes is None else t.phonemes) + t.whitespace for t in tokens)
        return result, tokens
