import phonemizer
import re
import platform

FROM_ESPEAKS = sorted({'\u0303':'','a^ɪ':'I','a^ʊ':'W','d^ʒ':'ʤ','e':'A','e^ɪ':'A','r':'ɹ','t^ʃ':'ʧ','x':'k','ç':'k','ɐ':'ə','ɔ^ɪ':'Y','ə^l':'ᵊl','ɚ':'əɹ','ɬ':'l','ʔ':'t','ʔn':'tᵊn','ʔˌn\u0329':'tᵊn','ʲ':'','ʲO':'jO','ʲQ':'jQ'}.items(), key=lambda kv: -len(kv[0]))

class EspeakFallback:
    def __init__(self, british):
        self.british = british
        system = platform.system()
        # hotfix for MacOS/Windows
        # https://github.com/bootphon/phonemizer/issues/44#issuecomment-1540885186
        if system == "Darwin":
            phonemizer.backend.espeak.wrapper.EspeakWrapper.set_library('/opt/homebrew/Cellar/espeak-ng/1.52.0/lib/libespeak-ng.1.dylib')
        elif system == "Windows":
            phonemizer.backend.espeak.wrapper.EspeakWrapper.set_library('C:\Program Files\eSpeak NG\libespeak-ng.dll')
        self.backend = phonemizer.backend.EspeakBackend(language=f"en-{'gb' if british else 'us'}", preserve_punctuation=True, with_stress=True, tie='^')

    def __call__(self, token):
        ps = self.backend.phonemize([token.text])
        if not ps:
            return None, None
        ps = ps[0].strip()
        for old, new in FROM_ESPEAKS:
            ps = ps.replace(old, new)
        ps = re.sub(r'(\S)\u0329', r'ᵊ\1', ps).replace(chr(809), '')
        if self.british:
            ps = ps.replace('e^ə', 'ɛː')
            ps = ps.replace('iə', 'ɪə')
            ps = ps.replace('ə^ʊ', 'Q')
        else:
            ps = ps.replace('o^ʊ', 'O')
            ps = ps.replace('ɜːɹ', 'ɜɹ')
            ps = ps.replace('ɜː', 'ɜɹ')
            ps = ps.replace('ɪə', 'iə')
            ps = ps.replace('ː', '')
        ps = ps.replace('o', 'ɔ') # for espeak < 1.52
        return ps.replace('^', ''), 2
