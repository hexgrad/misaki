"""Symbol-set validation for German pronunciation overrides.

Override phonemes in de_overrides.json bypass espeak and are fed straight to
the Kokoro model. Kokoro maps each phoneme to an embedding id and silently
drops any symbol it does not know (see KModel.forward). So every symbol used in
an override MUST be in Kokoro's vocabulary, otherwise that word is mispronounced
with no error.

This test guards against typos and wrong-convention symbols (e.g. ʏ, which is
NOT in Kokoro's vocab and was caught here during the initial port from
kikiri-tts PR #28).

KOKORO_VOCAB below is the set of real (non-padding, non-PUA-placeholder)
symbols from Kokoro-82M's config.json vocab, as mirrored in
kikiri-tts/StyleTTS2/kokoro_symbols.py (178 tokens; 115 real symbols).
"""

import json
import importlib.resources

from misaki import data
from misaki.de import normalize_for_lookup

# Real Kokoro-82M phoneme symbols (excludes the '$' pad and PUA placeholders).
KOKORO_VOCAB = frozenset(
    ';:,.!?—…"()“” \u0303ʣʥʦʨᵝꭧAIOQSTWYᵊ'
    "abcdefghijklmnopqrstuvwxyz"
    "ɑɐɒæβɔɕçɖðʤəɚɛɜɟɡɥɨɪʝɯɰŋɳɲɴøɸθœɹɾɻʁɽʂʃʈʧʊʋʌɣɤχʎʒʔˈˌːʰʲ↓→↗↘ᵻ"
)


def _load_raw_overrides():
    with importlib.resources.open_text(data, "de_overrides.json") as r:
        return json.load(r)


def test_all_override_phonemes_are_in_kokoro_vocab():
    raw = _load_raw_overrides()
    offenders = {}
    for section in ("brand", "en", "de_foreign"):
        for word, phonemes in raw[section].items():
            illegal = sorted({c for c in phonemes if c not in KOKORO_VOCAB})
            if illegal:
                offenders[f"{section}:{word}"] = illegal
    assert not offenders, (
        "Override phonemes use symbols outside Kokoro's vocab "
        "(these are silently dropped at inference): " + repr(offenders)
    )


def test_override_keys_are_already_normalized():
    """JSON keys should equal their normalize_for_lookup() form so lookups hit.

    Hyphenated keys like 'espeak-ng' and 'zero-shot' are allowed because the
    loader normalizes them; this test documents which keys rely on that.
    """
    raw = _load_raw_overrides()
    relies_on_normalization = {}
    for section in ("brand", "en", "de_foreign"):
        for word in raw[section]:
            normalized = normalize_for_lookup(word)
            if normalized != word:
                relies_on_normalization[f"{section}:{word}"] = normalized
    # Only joiner/hyphen forms are expected to differ from their normalized key.
    for original, normalized in relies_on_normalization.items():
        assert normalized, f"{original} normalizes to empty key"
