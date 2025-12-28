# Misaki French Phonemes

**Author**: Patrice
**License**: Apache 2.0

This document describes the phoneme inventory used by the Misaki French G2P module.

## Overview

French uses approximately **37 phonemes** including:
- 12 oral vowels
- 4 nasal vowels
- 3 semi-vowels (glides)
- 18 consonants

Unlike English, **French has no lexical stress** - stress is predictable (final syllable of a phrase). Therefore, stress marks (`ˈ`, `ˌ`) are not used.

## Phoneme Inventory

### Oral Vowels (12)

| IPA | Example | French Word | Notes |
|-----|---------|-------------|-------|
| i | /i/ | s**i**, l**i**t | close front unrounded |
| e | /e/ | ét**é**, n**e**z | close-mid front unrounded |
| ɛ | /ɛ/ | f**ai**t, p**è**re | open-mid front unrounded |
| a | /a/ | p**a**tte, l**à** | open front unrounded |
| ɑ | /ɑ/ | p**â**te | open back unrounded (rare) |
| ɔ | /ɔ/ | s**o**l, m**o**rt | open-mid back rounded |
| o | /o/ | s**o**t, **eau** | close-mid back rounded |
| u | /u/ | s**ou**s, g**oû**t | close back rounded |
| y | /y/ | s**u**, r**ue** | close front rounded |
| ø | /ø/ | f**eu**, d**eux** | close-mid front rounded |
| œ | /œ/ | s**eu**l, p**eu**r | open-mid front rounded |
| ə | /ə/ | l**e**, pr**e**mier | schwa (mid central) |

### Nasal Vowels (4)

| IPA | Example | French Word | Notes |
|-----|---------|-------------|-------|
| ɑ̃ | /ɑ̃/ | **an**, t**em**ps, v**en**t | open back nasal |
| ɛ̃ | /ɛ̃/ | v**in**, p**ain**, s**ein** | open-mid front nasal |
| ɔ̃ | /ɔ̃/ | b**on**, p**on**t | open-mid back nasal |
| œ̃ | /œ̃/ | br**un**, parf**um** | open-mid front rounded nasal |

> **Note**: In modern Parisian French, /œ̃/ is merging with /ɛ̃/. Many speakers pronounce "brun" as /bʁɛ̃/.

### Semi-Vowels / Glides (3)

| IPA | Example | French Word | Notes |
|-----|---------|-------------|-------|
| j | /j/ | **y**eux, f**i**lle | palatal approximant |
| w | /w/ | **ou**i, l**oi** | labio-velar approximant |
| ɥ | /ɥ/ | l**u**i, n**u**it | labio-palatal approximant |

### Consonants (18)

| IPA | Example | French Word | Notes |
|-----|---------|-------------|-------|
| p | /p/ | **p**as | voiceless bilabial plosive |
| b | /b/ | **b**as | voiced bilabial plosive |
| t | /t/ | **t**a | voiceless dental plosive |
| d | /d/ | **d**a | voiced dental plosive |
| k | /k/ | **c**as | voiceless velar plosive |
| ɡ | /ɡ/ | **g**are | voiced velar plosive |
| f | /f/ | **f**a | voiceless labiodental fricative |
| v | /v/ | **v**a | voiced labiodental fricative |
| s | /s/ | **s**a | voiceless alveolar fricative |
| z | /z/ | **z**oo | voiced alveolar fricative |
| ʃ | /ʃ/ | **ch**at | voiceless postalveolar fricative |
| ʒ | /ʒ/ | **j**our | voiced postalveolar fricative |
| m | /m/ | **m**a | bilabial nasal |
| n | /n/ | **n**a | alveolar nasal |
| ɲ | /ɲ/ | a**gn**eau | palatal nasal |
| ŋ | /ŋ/ | par**k**i**ng** | velar nasal (loanwords) |
| l | /l/ | **l**a | alveolar lateral |
| ʁ | /ʁ/ | **r**a | uvular fricative |

## Phoneme Mappings from espeak-ng

The module maps espeak-ng output to standardized IPA:

```python
E2K = {
    'ʀ': 'ʁ',  # Trill to fricative
    'r': 'ʁ',  # Alveolar to uvular
    'g': 'ɡ',  # ASCII to IPA g
}
```

## Comparison with English

| Feature | English | French |
|---------|---------|--------|
| Lexical stress | Yes (ˈ, ˌ) | No |
| Nasal vowels | No | Yes (4) |
| Front rounded vowels | No | Yes (y, ø, œ) |
| R sound | ɹ (alveolar) | ʁ (uvular) |
| Vowel length | Contrastive | Not contrastive |
| Diphthongs | Many | Few (oj, ɛj, etc.) |

## Common Pronunciation Patterns

### The "-ait/-ais" endings (imparfait)

These should be pronounced /ɛ/ (like "è"):

- était → /etɛ/
- faisait → /fəzɛ/
- savait → /savɛ/
- allait → /alɛ/

### The "-ain/-ein" endings (nasal)

These should be pronounced /ɛ̃/:

- main → /mɛ̃/
- plein → /plɛ̃/
- pain → /pɛ̃/

### Silent letters

French has many silent final consonants:

- fait → /fɛ/ (t silent)
- temps → /tɑ̃/ (ps silent)
- les → /le/ (s silent, unless liaison)

### Liaisons

Liaisons occur when a normally silent consonant is pronounced before a vowel:

- les amis → /le.z‿ami/
- un homme → /œ̃.n‿ɔm/

## References

- [French phonology - Wikipedia](https://en.wikipedia.org/wiki/French_phonology)
- [Help:IPA/French - Wikipedia](https://en.wikipedia.org/wiki/Help:IPA/French)
- [Appendix:French pronunciation - Wiktionary](https://en.wiktionary.org/wiki/Appendix:French_pronunciation)
