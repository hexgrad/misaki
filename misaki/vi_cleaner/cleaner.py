import re
import unicodedata

from .passage_utils import combine_passages, split_long_passages, split_text_passages

from .sentence_utils import get_pieces

from .letter_vi import normalize_letter_vi
from .currency_vi import normalize_currency_vi
from .acronym_vi import spell_acronyms_vi
from .numberical_vi import normalize_number_vi
from .measurement_vi import normalize_measurement_vi
from .datestime_vi import normalize_date, normalize_time
from .roman_number_vi import normalize_roman_numbers
from .abbreviation_vi import normalize_abbreviations_vi
from .symbol_vi import DEFAULT_PIECE_MAX_LENGTH, DEFAULT_SENTENCE_MAX_LENGTH, opening_brackets_and_punctutations_re, punctutations_re


class ViCleaner(object):
    def __init__(self, clean_abbr=True, clean_acronym=True):
        self.clean_abbr = clean_abbr
        self.clean_acronym = clean_acronym
        pass

    def join_lines(self, text):
        return text.replace("\n", " ")

    def _collapse_whitespace_before_punctuation(self, match):
        space, punctuation = match.groups(0)
        return punctuation

    def _collapse_whitespace_after_bracket(self, match):
        punctuation, space = match.groups(0)
        return space + punctuation

    def collapse_whitespace(self, text):
        text = re.sub(r"(\s)\1{1,}", r"\1", text)
        text = re.sub(punctutations_re,
                      self._collapse_whitespace_before_punctuation, text)
        text = re.sub(opening_brackets_and_punctutations_re,
                      self._collapse_whitespace_after_bracket, text)
        text = re.sub(r"(\s)\1{1,}", r"\1", text)
        text = re.sub(r"\t+", " ", text)
        text = text.strip()
        return text

    def lowercase(self, text):
        return text.lower()

    def clean_basic(self, text):
        text = self.collapse_whitespace(text)
        text = " " + text + " "
        return text

    def normalize_ascii_vi(self, text):
        return unicodedata.normalize("NFC", text)

    def expand_abbreviations(self, text):
        text = normalize_abbreviations_vi(text)
        return text

    def expand_acronyms(self, text):
        return spell_acronyms_vi(text)

    def expand_roman_numbers(self, text):
        return normalize_roman_numbers(text)

    def expand_date_time(self, text):
        text = normalize_date(text)
        text = normalize_time(text)
        return text

    def change_thang_bon_to_thang_tu(self, text):
        return re.sub("tháng bốn", "tháng tư", text, flags=re.IGNORECASE)

    def expand_measurement_units(self, text):
        return normalize_measurement_vi(text)

    def expand_currency(self, text):
        return normalize_currency_vi(text)

    def expand_number(self, text):
        return normalize_number_vi(text)

    def expand_letter(self, text):
        return normalize_letter_vi(text)

    def normalize_splash(self, text):
        text = re.sub(r"(/)", " trên ", text)
        return text

    def remove_left_hyphen(self, text):
        return re.sub(r"([^\s])(-)([^\s])", r"\1 \3", text)

    def normalize_linebreak(self, text):
        return [e.strip() for e in re.split(r'[\n]+', text)]

    def clean_text(self, text):
        text = self.collapse_whitespace(text)
        text = " " + text + " "

        text = self.normalize_ascii_vi(text)
        if self.clean_abbr:
            text = self.expand_abbreviations(text)
        text = self.expand_roman_numbers(text)
        if self.clean_acronym:
            text = self.expand_acronyms(text)
        text = self.expand_date_time(text)
        text = self.expand_measurement_units(text)
        text = self.expand_currency(text)
        text = self.expand_number(text)
        text = self.expand_letter(text)
        text = self.normalize_splash(text)
        text = self.remove_left_hyphen(text)

        text = self.collapse_whitespace(text)
        text = self.change_thang_bon_to_thang_tu(text)
        text = self.lowercase(text)
        return text

    def split_sentences(self, text=None, maxLength=DEFAULT_PIECE_MAX_LENGTH):
        text = text if (text is not None) else self.text
        text = re.sub("(?<![.!?])[\n]+", ".\n", text)
        passages = self.normalize_linebreak(text)
        result = []
        breaks = []
        for passage in passages:
            temp = get_pieces(passage, maxLength)
            result += temp
            if len(breaks) > 0:
                breaks += [breaks[-1]+len(temp)]
            else:
                breaks += [len(temp)]
        return result, breaks[0:len(breaks)-1]

    def split_passages(self, text=None, maxLength=DEFAULT_SENTENCE_MAX_LENGTH):
        text = text if (text is not None) else self.text
        passages = split_text_passages(text, r'[\n]+', False, "\n\t ")
        sub_passages = split_long_passages(passages, maxLength)

        combined_sub_passages = [combine_passages(
            i, maxLength) for i in sub_passages]
        sub_passages_lens = [len(i) for i in combined_sub_passages]
        breaks = [sum(sub_passages_lens[:i+1])
                  for i in range(len(sub_passages_lens))]
        flat_list = []

        for sublist in combined_sub_passages:
            for item in sublist:
                flat_list.append(item)
        result = combine_passages(flat_list, maxLength)
        return result, breaks