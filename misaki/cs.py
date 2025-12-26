#  SPDX-License-Identifier: Apache-2.0

# Grapheme to Phoneme for Czech language.
# Originaly developed by Richard Mazur
# https://github.com/essare-rimaz/grapheme_to_phoneme_CZ/blob/main/server.r
# Later converted to Python by Miroslav Suchy <msuchy@redhat.com> with
# assistence of AI. And with permission of Richard released under Apache-2.0
# license.

# Czech Phonology
# https://cs.wikipedia.org/wiki/Fonologie_%C4%8De%C5%A1tiny


from typing import Dict, List, Optional
from .token import MToken

IPA: Dict[str, str] = {
    "a": "a", "á": "aː", "b": "b", "c": "t͡s", "č": "t͡ʃ", "d": "d", "ď": "ɟ",
    "e": "ɛ", "é": "ɛː", "ě": "ě", "f": "f", "g": "ɡ", "h": "ɦ", "ch": "x",
    "i": "ɪ", "í": "iː", "j": "j", "k": "k", "l": "l", "m": "m", "n": "n",
    "ň": "ň", "o": "o", "ó": "oː", "p": "p", "q": "k", "r": "r", "s": "s",
    "š": "ʃ", "t": "t", "ť": "c", "u": "u", "ú": "uː", "ů": "uː", "v": "v",
    "w": "w", "x": "ks", "y": "ɪ", "ý": "iː", "z": "z", "ž": "ʒ",
    "di": "ɟɪ", "dí": "ɟiː", "dě": "ɟɛ",
    "ti": "cɪ", "tí": "ciː", "tě": "cɛ",
    "ni": "ɲɪ", "ní": "ɲiː", "ně": "ɲɛ",
    "mě": "mɲɛ", "bě": "bjɛ", "pě": "pjɛ", "vě": "vjɛ",
    "ts": "t͡s", "dz": "d͡z",
    "ie": "ɪjɛ", "ia": "ɪja", "io": "ɪjo",
    "ř": "r̝",
}

TEMP: Dict[str, str] = {
    "a": "a", "á": "á", "b": "b", "c": "c", "č": "č", "d": "d", "ď": "ď",
    "e": "e", "é": "é", "ě": "ě", "f": "f", "g": "g", "h": "h", "ch": "ch",
    "i": "i", "í": "í", "j": "j", "k": "k", "l": "l", "m": "m", "n": "n",
    "ň": "ň", "o": "o", "ó": "ó", "p": "p", "q": "q", "r": "r", "ř": "ř",
    "s": "s", "š": "š", "t": "t", "ť": "ť", "u": "u", "ú": "ú", "ů": "ů",
    "v": "v", "w": "w", "x": "x", "y": "y", "ý": "ý", "z": "z", "ž": "ž",
    "di": "di", "dí": "dí", "dě": "dě",
    "ti": "ti", "tí": "tí", "tě": "tě",
    "ni": "ni", "ní": "ní", "ně": "ně",
    "mě": "mě", "bě": "bě", "pě": "pě", "vě": "vě",
    "dz": "dz", "ts": "ts", "ie": "ie", "ia": "ia", "io": "io",
    " ": " ",
}

PAIRED_CONSONANTS: Dict[str, str] = {
    "b": "p", "d": "t", "ď": "ť", "g": "k", "v": "f", "z": "s", "ž": "š",
    "ch": "h", "dz": "c", "dž": "č",
    "p": "b", "t": "d", "ť": "ď", "k": "g", "f": "v", "s": "z", "š": "ž",
    "h": "ch", "c": "dz", "č": "dž",
}

PAIRED_UNVOICED: Dict[str, str] = {
    "p": "p", "t": "t", "ť": "ť", "k": "k", "f": "f", "s": "s", "š": "š",
    "ch": "ch", "c": "c", "č": "č",
}

PAIRED_VOICED: Dict[str, str] = {
    "b": "b", "d": "d", "ď": "ď", "g": "g", "v": "v", "z": "z", "ž": "ž",
    "dz": "dz", "dž": "dž",
}

DTN = {"d": "d", "t": "t", "n": "n"}
DTN_VOCAL = {"í": "í", "i": "i", "ě": "ě"}

MBPV = {"m": "m", "b": "b", "p": "p", "v": "v"}
MBPV_VOCAL = {"ě": "ě"}

CH_FIRST = {"c": "c"}
CH_SECOND = {"h": "h"}

TS_FIRST = {"t": "t"}
TS_SECOND = {"s": "s"}

DZ_FIRST = {"d": "d"}
DZ_SECOND = {"z": "z"}

IEIAIO_FIRST = {"i": "i"}
IEIAIO_SECOND = {"e": "e", "a": "a", "o": "o"}


def _indices_where_in(v: List[Optional[str]], keyset: Dict[str, str]) -> List[int]:
    """Mimics R: which(v %in% some_named_vector)."""
    s = set(keyset.keys())
    return [i for i, x in enumerate(v) if x in s]

class CSG2P:
    """ Grapheme to Phoneme for Czech language. """

    def __call__(self, text: str) -> Tuple[str, List[MToken]]:
        """
        Returns IPA string.
        """
        if text is None:
            return ""

        text = text.lower()
        text_split = list(text)

        result: List[Optional[str]] = []
        for ch in text_split:
            result.append(TEMP.get(ch))  # missing -> None (R NA)

        # 1) i followed by e/a/o => ie/ia/io
        for x in _indices_where_in(result, IEIAIO_FIRST):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in IEIAIO_SECOND:
                    result[x] = (result[x] or "") + (result[y] or "")
                    result[y] = None

        # 2) d + z => dz
        for x in _indices_where_in(result, DZ_FIRST):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in DZ_SECOND:
                    result[x] = (result[x] or "") + (result[y] or "")
                    result[y] = None

        # 3) t + s => ts
        for x in _indices_where_in(result, TS_FIRST):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in TS_SECOND:
                    result[x] = (result[x] or "") + (result[y] or "")
                    result[y] = None

        # 4) voicing assimilation: unvoiced before voiced => swap current with its pair
        for x in _indices_where_in(result, PAIRED_UNVOICED):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in PAIRED_VOICED:
                    w = result[x]
                    if w is not None and w in PAIRED_CONSONANTS:
                        result[x] = PAIRED_CONSONANTS[w]

        # 5) voicing assimilation: voiced before unvoiced => swap current with its pair
        for x in _indices_where_in(result, PAIRED_VOICED):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in PAIRED_UNVOICED:
                    w = result[x]
                    if w is not None and w in PAIRED_CONSONANTS:
                        result[x] = PAIRED_CONSONANTS[w]

        # 6) c + h => ch
        for x in _indices_where_in(result, CH_FIRST):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in CH_SECOND:
                    result[x] = (result[x] or "") + (result[y] or "")
                    result[y] = None

        # 7) d/t/n + (i/í/ě) => di/dí/dě, ti/tí/tě, ni/ní/ně
        for x in _indices_where_in(result, DTN):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in DTN_VOCAL:
                    result[x] = (result[x] or "") + (result[y] or "")
                    result[y] = None

        # 8) m/b/p/v + ě => mě/bě/pě/vě
        for x in _indices_where_in(result, MBPV):
            y = x + 1
            if y < len(result):
                z = result[y]
                if z is not None and z in MBPV_VOCAL:
                    result[x] = (result[x] or "") + (result[y] or "")
                    result[y] = None

        # Final devoicing: if last symbol is voiced, replace with its pair
        if result:
            last_idx = len(result) - 1
            z = result[last_idx]
            if z is not None and z in PAIRED_VOICED and z in PAIRED_CONSONANTS:
                result[last_idx] = PAIRED_CONSONANTS[z]

        # na.omit
        result_clean: List[str] = [x for x in result if x is not None]

        result_ipa: List[str] = []
        mtokens: list[MToken] = []
        for token in result_clean:
            result_ipa.append(TEMP.get(token, token))

        for i, token in enumerate(result_ipa):
            result_ipa[i] = IPA.get(token, token)
            mtokens.append(MToken(token, '', ' ', result_ipa[i]))

        return "".join(result_ipa), mtokens


if __name__ == "__main__":
    examples = ["odzbrojit se", "tsar", "filosofie", "nokia", "rio", "chata", "město", "běh"]
    g2p = CSG2P()
    for w in examples:
        print(w, "->", g2p(w)[0])
