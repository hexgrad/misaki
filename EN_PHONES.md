# Misaki English Phonemes

For English, Misaki currently uses 49 total phonemes. Of these, 41 are shared by both Americans and Brits, 4 are American-only, and 4 are British-only.

Disclaimer: Author is an ML researcher, not a linguist, and may have butchered or reappropriated the traditional meaning of some symbols. These symbols are intended as input tokens for neural networks to yield optimal performance.


### 🤝 Shared (41)

**Stress Marks (2)**
- `ˈ`: Primary stress, visually looks similar to an apostrophe.
- `ˌ`: Secondary stress.

**IPA Consonants (22)**
- `bdfhjklmnpstvwz`: 15 alpha consonants taken from IPA. They mostly sound as you'd expect, but `j` actually represents the "y" sound, like `yes => jˈɛs`.
- `ɡ`: Hard "g" sound, like `get => ɡɛt`. Visually looks like the lowercase letter g, but its actually `U+0261`.
- `ŋ`: The "ng" sound, like `sung => sˈʌŋ`.
- `ɹ`: Upside-down r is just an "r" sound, like `red => ɹˈɛd`.
- `ʃ`: The "sh" sound, like `shin => ʃˈɪn`.
- `ʒ`: The "zh" sound, like `Asia => ˈAʒə`.
- `ð`: Soft "th" sound, like `than => ðən`.
- `θ`: Hard "th" sound, like `thin => θˈɪn`.

**Consonant Clusters (2)**
- `ʤ`: A "j" or "dg" sound, merges `dʒ`, like `jump => ʤˈʌmp` or `lunge => lˈʌnʤ`.
- `ʧ`: The "ch" sound, merges `tʃ`, like `chump => ʧˈʌmp` or `lunch => lˈʌnʧ`.

**IPA Vowels (10)**
- `ə`: The schwa is a common, unstressed vowel sound, like `a 🍌 => ə 🍌`.
- `i`: As in `easy => ˈizi`.
- `u`: As in `flu => flˈu`.
- `ɑ`: As in `spa => spˈɑ`.
- `ɔ`: As in `all => ˈɔl`.
- `ɛ`: As in `hair => hˈɛɹ` or `bed => bˈɛd`. Possibly dubious, because those vowel sounds do not sound similar to my ear.
- `ɜ`: As in `her => hɜɹ`. Easy to confuse with `ɛ` above.
- `ɪ`: As in `brick => bɹˈɪk`.
- `ʊ`: As in `wood => wˈʊd`.
- `ʌ`: As in `sun => sˈʌn`.

**Diphthong Vowels (4)**
- `A`: The "eh" vowel sound, like `hey => hˈA`. Expands to `eɪ` in IPA.
- `I`: The "eye" vowel sound, like `high => hˈI`. Expands to `aɪ` in IPA.
- `W`: The "ow" vowel sound, like `how => hˌW`. Expands to `aʊ` in IPA.
- `Y`: The "oy" vowel sound, like `soy => sˈY`. Expands to `ɔɪ` in IPA.

**Custom Vowel (1)**
- `ᵊ`: Small schwa, muted version of `ə`, like `pixel => pˈɪksᵊl`. I made this one up, so I'm not entirely sure if it's correct.


### 🇺🇸 American-only (4)

**Vowels (3)**
- `æ`: The vowel sound at the start of `ash => ˈæʃ`.
- `O`: Capital letter representing the American "oh" vowel sound. Expands to `oʊ` in IPA.
- `ᵻ`: A sound somewhere in between `ə` and `ɪ`, often used in certain -s suffixes like `boxes => bˈɑksᵻz`.

**Consonant (1)**
- `ɾ`: A sound somewhere in between `t` and `d`, like `butter => bˈʌɾəɹ`.


### 🇬🇧 British-only (4)

**Vowels (3)**
- `a`: The vowel sound at the start of `ash => ˈaʃ`.
- `Q`: Capital letter representing the British "oh" vowel sound. Expands to `əʊ` in IPA.
- `ɒ`: The sound at the start of `on => ˌɒn`. Easy to confuse with `ɑ`, which is a shared phoneme.

**Other (1)**
- `ː`: Vowel extender, visually looks similar to a colon. Possibly dubious, because Americans extend vowels too, but the gold US dictionary somehow lacks these. Often used by the Brits instead of `ɹ`: Americans say `or => ɔɹ`, but Brits say `or => ɔː`.


### ♻️ From espeak to Misaki
```py
import re
FROM_ESPEAKS = sorted({'\u0303':'','a^ɪ':'I','a^ʊ':'W','d^ʒ':'ʤ','e':'A','e^ɪ':'A','r':'ɹ','t^ʃ':'ʧ','x':'k','ç':'k','ɐ':'ə','ɔ^ɪ':'Y','ə^l':'ᵊl','ɚ':'əɹ','ɬ':'l','ʔ':'t','ʔn':'tᵊn','ʔˌn\u0329':'tᵊn','ʲ':'','ʲO':'jO','ʲQ':'jQ'}.items(), key=lambda kv: -len(kv[0]))
def from_espeak(ps, british):
    for old, new in FROM_ESPEAKS:
        ps = ps.replace(old, new)
    ps = re.sub(r'(\S)\u0329', r'ᵊ\1', ps).replace(chr(809), '')
    if british:
        ps = ps.replace('e^ə', 'ɛː')
        ps = ps.replace('iə', 'ɪə')
        ps = ps.replace('ə^ʊ', 'Q')
    else:
        ps = ps.replace('o^ʊ', 'O')
        ps = ps.replace('ɜːɹ', 'ɜɹ')
        ps = ps.replace('ɜː', 'ɜɹ')
        ps = ps.replace('ɪə', 'iə')
        ps = ps.replace('ː', '')
    return ps.replace('^', '')

import phonemizer
british = False
espeak = phonemizer.backend.EspeakBackend(
    language=f"en-{'gb' if british else 'us'}",
    preserve_punctuation=True, with_stress=True, tie='^'
)
text = 'merchantship'
espeak_ps = espeak.phonemize([text])
espeak_ps = espeak_ps[0].strip() if espeak_ps else ''
assert espeak_ps == 'mˈɜːt^ʃəntʃˌɪp', espeak_ps
ps = from_espeak(espeak_ps, british)
assert ps == ('mˈɜːʧəntʃˌɪp' if british else 'mˈɜɹʧəntʃˌɪp'), ps
VOCAB = frozenset('AIWYbdfhijklmnpstuvwzðŋɑɔəɛɜɡɪɹʃʊʌʒʤʧˈˌθᵊ' + ('Qaɒː' if british else 'Oæɾᵻ'))
assert len(VOCAB) == 45, len(VOCAB)
assert all(p in VOCAB for p in ps), ps
```


### ♻️ Misaki to espeak
```py
def to_espeak(ps):
    # Optionally, you can add a tie character in between the 2 replacement characters.
    ps = ps.replace('ʤ', 'dʒ').replace('ʧ', 'tʃ')
    ps = ps.replace('A', 'eɪ').replace('I', 'aɪ').replace('Y', 'ɔɪ')
    ps = ps.replace('O', 'oʊ').replace('Q', 'əʊ').replace('W', 'aʊ')
    return ps.replace('ᵊ', 'ə')
```
