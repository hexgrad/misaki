"""
Phonemize Hebrew using mishkal package from https://github.com/thewh1teagle/phonikud
"""

import phonikud

class HEG2P:
    def __call__(self, text: str, preserve_punctuation = True, preserve_stress = True, **kwargs):
        """
        Convert Hebrew text to IPA
        Text is expected to be with enhanced diacritics (nikud)
        """

        return phonikud.phonemize(text, preserve_punctuation=preserve_punctuation, preserve_stress=preserve_stress, **kwargs)