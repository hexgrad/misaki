"""
Phonemize Hebrew using mishkal package from https://github.com/thewh1teagle/mishkal
"""

import mishkal

class HEG2P:
    def __call__(self, text: str, preserve_punctuation = True, preserve_stress = True):
        """
        Convert Hebrew text to IPA
        Text is expected to be with diacritics (niqqud)
        Enable debug to return Word objects that contais detailed conversion information
        """

        return mishkal.phonemize(text, preserve_punctuation=preserve_punctuation, preserve_stress=preserve_stress)

    def get_phonene_set(self):
        """
        Return list with exact phonemes used in mishkal package
        """

        return mishkal.get_phoneme_set()