# misaki
Misaki is a G2P engine designed for [Kokoro](https://github.com/hexgrad/kokoro) models.

Hosted demo: https://hf.co/spaces/hexgrad/Misaki-G2P

### English Usage
You can run this in one cell on [Google Colab](https://colab.research.google.com/):
```py
!pip install -q "misaki[en]"

from misaki import en

g2p = en.G2P(trf=False, british=False, fallback=None) # no transformer, American English

text = '[Misaki](/misˈɑki/) is a G2P engine designed for [Kokoro](/kˈOkəɹO/) models.'

phonemes, tokens = g2p(text)

print(phonemes) # misˈɑki ɪz ə ʤˈitəpˈi ˈɛnʤən dəzˈInd fɔɹ kˈOkəɹO mˈɑdᵊlz.
```

To fallback to espeak:
```py
# Installing espeak varies across platforms, this silent install works on Colab:
!apt-get -qq -y install espeak-ng > /dev/null 2>&1

!pip install -q "misaki[en]" phonemizer-fork

from misaki import en, espeak

fallback = espeak.EspeakFallback(british=False) # en-us

g2p = en.G2P(trf=False, british=False, fallback=fallback) # no transformer, American English

text = 'Now outofdictionary words are handled by espeak.'

phonemes, tokens = g2p(text)

print(phonemes) # nˈW Wɾɑfdˈɪkʃənˌɛɹi wˈɜɹdz ɑɹ hˈændəld bI ˈispik.
```

### English
- https://github.com/explosion/spaCy
- https://github.com/savoirfairelinux/num2words
- https://github.com/hexgrad/misaki/blob/main/EN_PHONES.md

### Japanese
The second gen Japanese tokenizer now uses pyopenjtalk with full unidic, enabling pitch accent marks and improved phrase merging. Deep gratitude to [@sophiefy](https://github.com/sophiefy) for invaluable recommendations and nuanced help with pitch accent.
- https://github.com/r9y9/pyopenjtalk
- https://github.com/polm/unidic-py

The first gen Japanese tokenizer mainly relies on cutlet => fugashi => mecab => unidic-lite, with each being a wrapper around the next. Deep gratitute to [@Respaired](https://github.com/Respaired) for helping me learn the ropes of Japanese tokenization before any Kokoro model had started training.
- https://github.com/polm/cutlet
- https://github.com/polm/fugashi
- https://github.com/ikegami-yukino/jaconv
- https://github.com/studio-ousia/mojimoji

### Korean
The Korean tokenizer is copied from 5Hyeons's g2pkc fork of Kyubyong's widely used g2pK library. Deep gratitute to [@5Hyeons](https://github.com/5Hyeons) for kindly helping with Korean and extending the original code by [@Kyubyong](https://github.com/Kyubyong).
- https://github.com/5Hyeons/StyleTTS2/tree/vocos/g2pK/g2pkc
- https://github.com/Kyubyong/g2pK

### Chinese
The second gen Chinese tokenizer adapts better logic from paddlespeech's frontend. Jieba now cuts and tags, and pinyin-to-ipa is no longer used.
- https://github.com/PaddlePaddle/PaddleSpeech/tree/develop/paddlespeech/t2s/frontend

The first gen Chinese tokenizer uses jieba to cut, pypinyin, and pinyin-to-ipa.
- https://github.com/fxsjy/jieba
- https://github.com/mozillazg/python-pinyin
- https://github.com/stefantaubert/pinyin-to-ipa

### Vietnamese
- https://github.com/v-nhandt21/Viphoneme

### TODO
- [ ] Data: Compress [data](https://github.com/hexgrad/misaki/tree/main/misaki/data) (no need for indented json) and eliminate redundancy between gold and silver dictionaries.
- [ ] Fallbacks: Train seq2seq fallback models on dictionaries using [this notebook](https://github.com/Kyubyong/nlp_made_easy/blob/master/PyTorch%20seq2seq%20template%20based%20on%20the%20g2p%20task.ipynb).
- [ ] Homographs: Escalate hard words like `axes bass bow lead tear wind` using BERT contextual word embeddings (CWEs) and logistic regression (LR) models (`nn.Linear` followed by sigmoid) as described in [this paper](https://assets.amazon.science/c3/db/23ca18d7450d8dbb5b80a11fcdd3/homograph-disambiguation-with-contextual-word-embeddings-for-tts-systems.pdf). Assuming `trf=True`, BERT CWEs can be accessed via `doc._.trf_data`, see [en.py#L479](https://github.com/hexgrad/misaki/blob/main/misaki/en.py#L479). Per-word LR models can be trained on [WikipediaHomographData](https://github.com/google-research-datasets/WikipediaHomographData), [llama-hd-dataset](https://github.com/facebookresearch/llama-hd-dataset), and LLM-generated data.
- [x] More languages: Add `ko.py`, `ja.py`, `zh.py`.
- [x] Per-language pip installs

### Acknowledgements
- 🛠️ Misaki builds on top of many excellent G2P projects linked above.
- 🌐 Thank you to all native speakers who advised and contributed G2P in many languages.
- 👾 Kokoro Discord server: https://discord.gg/QuGxSWBfQy
- 🌸 Misaki is a Japanese name and a [character in the Terminator franchise](https://terminator.fandom.com/wiki/Misaki) along with [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file#acknowledgements).

<img src="https://static.wikia.nocookie.net/terminator/images/2/2e/Character_Misaki.png/revision/latest?cb=20240914020038" width="400" alt="misaki" />
