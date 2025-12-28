"""
Misaki French G2P Module

A Grapheme-to-Phoneme engine for French, designed for Kokoro TTS models.

Author: Patrice (contributed via Claude Code)
License: Apache 2.0

Features:
- French pronunciation dictionary (fr_gold.json)
- Abbreviation and number expansion
- Liaison hints
- Elision handling
- espeak-ng fallback for unknown words
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Union

# Optional imports
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from phonemizer.backend import EspeakBackend
    from phonemizer.separator import Separator
    PHONEMIZER_AVAILABLE = True
except ImportError:
    PHONEMIZER_AVAILABLE = False


# =============================================================================
# FRENCH PHONEME INVENTORY
# =============================================================================

# Oral vowels
ORAL_VOWELS = {
    'i',   # si, lit
    'e',   # été, nez
    'ɛ',   # fait, père, rêve
    'a',   # patte, là
    'ɑ',   # pâte (rare, merging with /a/)
    'ɔ',   # sol, mort
    'o',   # sot, eau
    'u',   # sous, goût
    'y',   # su, rue
    'ø',   # feu, deux
    'œ',   # seul, peur
    'ə',   # le, premier (schwa)
}

# Nasal vowels
NASAL_VOWELS = {
    'ɑ̃',  # an, temps, vent
    'ɛ̃',  # vin, pain, sein
    'ɔ̃',  # bon, pont
    'œ̃',  # brun, parfum (merging with ɛ̃ in modern French)
}

# Semi-vowels (glides)
SEMI_VOWELS = {
    'j',   # yeux, fille
    'w',   # oui, loi
    'ɥ',   # lui, nuit
}

# Consonants
CONSONANTS = {
    'p', 'b',      # pas, bas
    't', 'd',      # ta, da
    'k', 'ɡ',      # cas, gare
    'f', 'v',      # fa, va
    's', 'z',      # sa, zoo
    'ʃ', 'ʒ',      # chat, jour
    'm', 'n',      # ma, na
    'ɲ',           # agneau
    'ŋ',           # parking (loanwords)
    'l',           # la
    'ʁ',           # ra (uvular R)
}

# All French phonemes
PHONEMES = ORAL_VOWELS | NASAL_VOWELS | SEMI_VOWELS | CONSONANTS

# For Kokoro compatibility, we may need to map some phonemes
# espeak-ng to Kokoro mapping
E2K = {
    # Nasal vowels (espeak uses combining tilde)
    'ɑ̃': 'ɑ̃',
    'ɛ̃': 'ɛ̃',
    'ɔ̃': 'ɔ̃',
    'œ̃': 'œ̃',
    # R variants
    'ʀ': 'ʁ',
    'r': 'ʁ',
    'ɹ': 'ʁ',
    # Other normalizations
    'ɡ': 'ɡ',  # ensure correct g
    'g': 'ɡ',
}


# =============================================================================
# FRENCH LEXICON
# =============================================================================

@dataclass
class MToken:
    """Token with pronunciation metadata."""
    text: str
    phonemes: Optional[str] = None
    rating: int = 0  # 0=unknown, 1=fallback, 2=espeak, 3=silver, 4=gold
    pos: Optional[str] = None

    def __repr__(self):
        return f"MToken({self.text!r}, ph={self.phonemes!r}, r={self.rating})"


class FrenchLexicon:
    """
    French pronunciation dictionary with morphological analysis.

    Rating system:
    - 4: Gold dictionary (verified pronunciations)
    - 3: Silver dictionary (auto-generated, less reliable)
    - 2: espeak-ng fallback
    - 1: Guessed/unknown
    """

    # Characters allowed in lexicon entries
    VALID_CHARS = set("abcdefghijklmnopqrstuvwxyzàâäéèêëïîôùûüœæç'-")

    # Common French abbreviations
    ABBREVIATIONS = {
        # Titles
        "M.": "monsieur",
        "Mme": "madame",
        "Mlle": "mademoiselle",
        "Dr": "docteur",
        "Pr": "professeur",
        "Me": "maître",
        "Mgr": "monseigneur",
        "St": "saint",
        "Ste": "sainte",

        # Common abbreviations
        "etc.": "et cetera",
        "cf.": "confer",
        "ex.": "exemple",
        "n°": "numéro",
        "N°": "numéro",
        "p.": "page",
        "pp.": "pages",
        "vol.": "volume",
        "chap.": "chapitre",
        "éd.": "édition",
        "env.": "environ",
        "min.": "minute",
        "sec.": "seconde",
        "h": "heure",
        "km": "kilomètre",
        "m": "mètre",
        "cm": "centimètre",
        "mm": "millimètre",
        "kg": "kilogramme",
        "g": "gramme",
        "mg": "milligramme",
        "l": "litre",
        "ml": "millilitre",

        # Organizations
        "ONU": "O N U",
        "UE": "U E",
        "USA": "U S A",
        "SNCF": "S N C F",
        "TGV": "T G V",
        "RER": "R E R",
        "RATP": "R A T P",
    }

    # Currency symbols
    CURRENCIES = {
        "€": "euro",
        "$": "dollar",
        "£": "livre",
        "¥": "yen",
        "CHF": "franc suisse",
    }

    # Ordinal suffixes
    ORDINALS = {
        "1er": "premier",
        "1ère": "première",
        "1re": "première",
        "2e": "deuxième",
        "2ème": "deuxième",
        "2nd": "second",
        "2nde": "seconde",
        "3e": "troisième",
        "3ème": "troisième",
    }

    def __init__(self, gold_path: Optional[Path] = None, silver_path: Optional[Path] = None):
        """
        Initialize the French lexicon.

        Args:
            gold_path: Path to gold dictionary JSON
            silver_path: Path to silver dictionary JSON
        """
        self.gold = {}
        self.silver = {}

        # Load dictionaries if provided
        if gold_path and gold_path.exists():
            with open(gold_path, 'r', encoding='utf-8') as f:
                self.gold = json.load(f)

        if silver_path and silver_path.exists():
            with open(silver_path, 'r', encoding='utf-8') as f:
                self.silver = json.load(f)

        # Built-in pronunciation fixes (high priority)
        self._init_builtin_fixes()

    def _init_builtin_fixes(self):
        """Initialize built-in pronunciation corrections."""
        # These override espeak-ng pronunciations for common errors
        self.builtin = {
            # Verbs with -ait/-ais (imparfait) - often mispronounced
            "était": "etɛ",
            "étais": "etɛ",
            "étaient": "etɛ",
            "avait": "avɛ",
            "avais": "avɛ",
            "avaient": "avɛ",
            "fait": "fɛ",
            "fais": "fɛ",
            "faite": "fɛt",
            "faites": "fɛt",
            "savait": "savɛ",
            "savais": "savɛ",
            "disait": "dizɛ",
            "faisait": "fəzɛ",
            "allait": "alɛ",
            "venait": "vənɛ",
            "devait": "dəvɛ",
            "pouvait": "puvɛ",
            "voulait": "vulɛ",
            "voyait": "vwajɛ",
            "croyait": "kʁwajɛ",
            "parlait": "paʁlɛ",
            "donnait": "dɔnɛ",
            "pensait": "pɑ̃sɛ",
            "restait": "ʁɛstɛ",
            "passait": "pasɛ",
            "trouvait": "tʁuvɛ",
            "regardait": "ʁəɡaʁdɛ",
            "écoutait": "ekutɛ",
            "attendait": "atɑ̃dɛ",
            "semblait": "sɑ̃blɛ",
            "paraissait": "paʁɛsɛ",
            "connaissait": "kɔnɛsɛ",
            "redoublait": "ʁədublɛ",
            "grondait": "ɡʁɔ̃dɛ",

            # Words with -ai-
            "maîtriser": "mɛtʁize",
            "maitriser": "mɛtʁize",
            "maîtrise": "mɛtʁiz",
            "commissaire": "kɔmisɛʁ",
            "affaire": "afɛʁ",
            "faire": "fɛʁ",
            "plaire": "plɛʁ",
            "taire": "tɛʁ",
            "ordinaire": "ɔʁdinɛʁ",
            "extraordinaire": "ɛkstʁaɔʁdinɛʁ",
            "éclair": "eklɛʁ",
            "chair": "ʃɛʁ",
            "pair": "pɛʁ",
            "clair": "klɛʁ",

            # "aime" and derivatives
            "aime": "ɛm",
            "aimes": "ɛm",
            "aiment": "ɛm",
            "aimait": "ɛmɛ",
            "aimais": "ɛmɛ",

            # Words with -ain/-ein (nasal)
            "main": "mɛ̃",
            "mains": "mɛ̃",
            "demain": "dəmɛ̃",
            "maintenant": "mɛ̃tnɑ̃",
            "certain": "sɛʁtɛ̃",
            "certaine": "sɛʁtɛn",
            "humain": "ymɛ̃",
            "humaine": "ymɛn",
            "soudain": "sudɛ̃",
            "prochain": "pʁɔʃɛ̃",
            "train": "tʁɛ̃",
            "plein": "plɛ̃",
            "frein": "fʁɛ̃",

            # Common words
            "monsieur": "məsjø",
            "messieurs": "mesjø",
            "madame": "madam",
            "mademoiselle": "madmwazɛl",
            "aujourd'hui": "oʒuʁdɥi",

            # Silent letters and liaisons
            "les": "le",
            "des": "de",
            "est": "ɛ",
            "et": "e",
        }

    def get(self, word: str, pos: Optional[str] = None) -> Optional[Tuple[str, int]]:
        """
        Get pronunciation for a word.

        Args:
            word: Word to look up
            pos: Part-of-speech tag (optional)

        Returns:
            Tuple of (phonemes, rating) or None if not found
        """
        word_lower = word.lower()

        # Check built-in fixes first (highest priority after gold)
        if word_lower in self.builtin:
            return (self.builtin[word_lower], 4)

        # Check gold dictionary
        if word_lower in self.gold:
            entry = self.gold[word_lower]
            if isinstance(entry, dict) and pos:
                phonemes = entry.get(pos, entry.get("DEFAULT", None))
            else:
                phonemes = entry if isinstance(entry, str) else entry.get("DEFAULT")
            if phonemes:
                return (phonemes, 4)

        # Check silver dictionary
        if word_lower in self.silver:
            entry = self.silver[word_lower]
            phonemes = entry if isinstance(entry, str) else entry.get("DEFAULT")
            if phonemes:
                return (phonemes, 3)

        return None

    def expand_abbreviation(self, text: str) -> str:
        """Expand common French abbreviations."""
        for abbr, expansion in self.ABBREVIATIONS.items():
            # Use word boundaries
            pattern = re.escape(abbr)
            if abbr.endswith('.'):
                text = re.sub(rf'\b{pattern}(?=\s|$|[,;:!?])', expansion, text, flags=re.IGNORECASE)
            else:
                text = re.sub(rf'\b{pattern}\b', expansion, text, flags=re.IGNORECASE)
        return text

    def expand_ordinals(self, text: str) -> str:
        """Expand ordinal numbers."""
        for ordinal, expansion in self.ORDINALS.items():
            text = re.sub(rf'\b{re.escape(ordinal)}\b', expansion, text, flags=re.IGNORECASE)
        return text


# =============================================================================
# NUMBER TO FRENCH WORDS
# =============================================================================

def number_to_french(n: int) -> str:
    """
    Convert a number to French words.

    Args:
        n: Integer to convert (supports up to millions)

    Returns:
        French word representation
    """
    if n < 0:
        return "moins " + number_to_french(-n)

    if n == 0:
        return "zéro"

    units = ['', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf',
             'dix', 'onze', 'douze', 'treize', 'quatorze', 'quinze', 'seize', 'dix-sept',
             'dix-huit', 'dix-neuf']
    tens = ['', '', 'vingt', 'trente', 'quarante', 'cinquante', 'soixante',
            'soixante', 'quatre-vingt', 'quatre-vingt']

    if n < 20:
        return units[n]

    if n < 100:
        t, u = divmod(n, 10)
        if t == 7 or t == 9:
            u += 10
            t -= 1
        if u == 0:
            suffix = 's' if t == 8 else ''
            return tens[t] + suffix
        elif u == 1 and t not in [8, 9]:
            return tens[t] + '-et-un'
        else:
            return tens[t] + '-' + units[u]

    if n < 1000:
        c, r = divmod(n, 100)
        if c == 1:
            prefix = 'cent'
        else:
            prefix = units[c] + '-cent'
        if r == 0:
            return prefix + ('s' if c > 1 else '')
        return prefix + '-' + number_to_french(r)

    if n < 1000000:
        m, r = divmod(n, 1000)
        if m == 1:
            prefix = 'mille'
        else:
            prefix = number_to_french(m) + '-mille'
        if r == 0:
            return prefix
        return prefix + '-' + number_to_french(r)

    if n < 1000000000:
        m, r = divmod(n, 1000000)
        if m == 1:
            prefix = 'un-million'
        else:
            prefix = number_to_french(m) + '-millions'
        if r == 0:
            return prefix
        return prefix + '-' + number_to_french(r)

    return str(n)


def expand_numbers(text: str, max_value: int = 1000000) -> str:
    """
    Expand numbers in text to French words.

    Args:
        text: Text containing numbers
        max_value: Maximum value to expand (larger numbers kept as-is)

    Returns:
        Text with numbers expanded
    """
    def replace_match(match):
        num = int(match.group(0))
        if num <= max_value:
            return number_to_french(num)
        return match.group(0)

    return re.sub(r'\b\d+\b', replace_match, text)


# =============================================================================
# FRENCH TEXT PREPROCESSOR
# =============================================================================

class FrenchPreprocessor:
    """
    Preprocessor for French text before G2P conversion.

    Handles:
    - Unicode normalization
    - Abbreviation expansion
    - Number expansion
    - Punctuation normalization
    """

    # Punctuation normalization
    PUNCT_MAP = {
        '«': '"',
        '»': '"',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '—': '-',
        '–': '-',
        '…': '...',
    }

    def __init__(self, lexicon: Optional[FrenchLexicon] = None):
        self.lexicon = lexicon or FrenchLexicon()

    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters."""
        import unicodedata
        # Use NFC to keep accented characters composed
        return unicodedata.normalize('NFC', text)

    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation marks."""
        for old, new in self.PUNCT_MAP.items():
            text = text.replace(old, new)
        # Remove non-breaking spaces
        text = text.replace('\u00A0', ' ')
        text = text.replace('\u202F', ' ')
        # Collapse multiple spaces
        text = re.sub(r' +', ' ', text)
        return text

    def expand_time(self, text: str) -> str:
        """Expand time expressions like 14h30."""
        def replace_time(match):
            hours = int(match.group(1))
            minutes = match.group(2)
            result = number_to_french(hours) + " heure"
            if hours > 1:
                result += "s"
            if minutes:
                mins = int(minutes)
                if mins > 0:
                    result += " " + number_to_french(mins)
            return result

        return re.sub(r'\b(\d{1,2})h(\d{2})?\b', replace_time, text)

    def process(self, text: str, expand_nums: bool = True) -> str:
        """
        Full preprocessing pipeline.

        Args:
            text: Raw text input
            expand_nums: Whether to expand numbers to words

        Returns:
            Preprocessed text ready for G2P
        """
        text = self.normalize_unicode(text)
        text = self.normalize_punctuation(text)
        text = self.lexicon.expand_abbreviation(text)
        text = self.lexicon.expand_ordinals(text)
        text = self.expand_time(text)

        if expand_nums:
            text = expand_numbers(text)

        return text.strip()


# =============================================================================
# ESPEAK FALLBACK
# =============================================================================

class EspeakFallback:
    """
    Fallback G2P using espeak-ng for unknown words.
    """

    def __init__(self):
        if not PHONEMIZER_AVAILABLE:
            raise ImportError("phonemizer is required for EspeakFallback")

        self.backend = EspeakBackend(
            language='fr-fr',
            with_stress=False,  # French doesn't have lexical stress
            tie='^'
        )
        self.separator = Separator(phone=' ', word=' ', syllable='')

    def __call__(self, text: str) -> Tuple[str, int]:
        """
        Convert text to phonemes using espeak-ng.

        Returns:
            Tuple of (phonemes, rating=2)
        """
        try:
            phonemes = self.backend.phonemize([text], separator=self.separator)[0]
            # Clean up
            phonemes = phonemes.strip()
            phonemes = re.sub(r'\s+', ' ', phonemes)
            # Apply mappings
            for old, new in E2K.items():
                phonemes = phonemes.replace(old, new)
            return (phonemes, 2)
        except Exception:
            return (text, 1)


# =============================================================================
# MAIN G2P CLASS
# =============================================================================

class G2P:
    """
    French Grapheme-to-Phoneme converter.

    Usage:
        g2p = G2P()
        phonemes, tokens = g2p("Bonjour, comment allez-vous?")

    Args:
        use_spacy: Use spaCy for tokenization (recommended)
        fallback: Use espeak-ng for unknown words
    """

    def __init__(
        self,
        use_spacy: bool = True,
        fallback: bool = True,
        gold_path: Optional[Path] = None,
        silver_path: Optional[Path] = None
    ):
        self.lexicon = FrenchLexicon(gold_path, silver_path)
        self.preprocessor = FrenchPreprocessor(self.lexicon)

        # Initialize spaCy
        self.nlp = None
        if use_spacy and SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("fr_core_news_sm")
            except OSError:
                print("Warning: fr_core_news_sm not found. Install with: python -m spacy download fr_core_news_sm")

        # Initialize fallback
        self.fallback = None
        if fallback and PHONEMIZER_AVAILABLE:
            try:
                self.fallback = EspeakFallback()
            except Exception as e:
                print(f"Warning: espeak fallback not available: {e}")

    def tokenize(self, text: str) -> List[MToken]:
        """
        Tokenize text into MTokens.

        Uses spaCy if available, otherwise simple regex tokenization.
        """
        if self.nlp:
            doc = self.nlp(text)
            return [MToken(text=token.text, pos=token.pos_) for token in doc]
        else:
            # Simple fallback tokenization
            tokens = re.findall(r"[\w']+|[^\w\s]", text, re.UNICODE)
            return [MToken(text=t) for t in tokens]

    def phonemize_token(self, token: MToken) -> MToken:
        """
        Convert a single token to phonemes.
        """
        text = token.text

        # Skip punctuation
        if re.match(r'^[^\w]+$', text, re.UNICODE):
            token.phonemes = text
            token.rating = 4
            return token

        # Try lexicon lookup
        result = self.lexicon.get(text, token.pos)
        if result:
            token.phonemes, token.rating = result
            return token

        # Try fallback
        if self.fallback:
            token.phonemes, token.rating = self.fallback(text)
            return token

        # Unknown word
        token.phonemes = text
        token.rating = 1
        return token

    def __call__(self, text: str, preprocess: bool = True) -> Tuple[str, List[MToken]]:
        """
        Convert text to phonemes.

        Args:
            text: Input text
            preprocess: Apply preprocessing (abbreviations, numbers, etc.)

        Returns:
            Tuple of (phoneme_string, list_of_tokens)
        """
        # Preprocess
        if preprocess:
            text = self.preprocessor.process(text)

        # Tokenize
        tokens = self.tokenize(text)

        # Phonemize each token
        for token in tokens:
            self.phonemize_token(token)

        # Build output string
        phonemes = ' '.join(t.phonemes for t in tokens if t.phonemes)

        # Clean up spacing around punctuation
        phonemes = re.sub(r'\s+([.,!?;:])', r'\1', phonemes)
        phonemes = re.sub(r'\s+', ' ', phonemes)

        return phonemes.strip(), tokens


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def phonemize(text: str, **kwargs) -> str:
    """
    Quick phonemization of French text.

    Args:
        text: French text to phonemize
        **kwargs: Arguments passed to G2P

    Returns:
        Phoneme string
    """
    g2p = G2P(**kwargs)
    phonemes, _ = g2p(text)
    return phonemes


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MISAKI FRENCH G2P - Test")
    print("=" * 60)

    g2p = G2P()

    tests = [
        "Bonjour, comment allez-vous?",
        "C'était une belle journée d'été.",
        "Il fait beau aujourd'hui.",
        "J'aime le café au lait.",
        "Le commissaire Dupont arriva à 14h30.",
        "M. Martin et Mme Dubois sont là.",
        "Elle savait qu'il faisait attention.",
        "Ses mains tremblaient de froid.",
        "Le train partira demain matin.",
    ]

    for text in tests:
        phonemes, tokens = g2p(text)
        print(f"\nInput:    {text}")
        print(f"Phonemes: {phonemes}")
        print(f"Tokens:   {[(t.text, t.rating) for t in tokens[:5]]}...")
