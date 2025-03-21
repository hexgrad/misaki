
import re

from .symbol_vi import punctuations

def isTextOnly(c: str):
    return c.isalnum()

def split_text_sentences(text, regex):
    return [e.strip() + d for e, d in zip(re.split(regex, text), re.findall(regex, text)) if e]

def combine_sentences(sentences: list, maxLength: int = 30) -> list:
        if len(sentences) <= 1:
            return sentences
        if len(sentences[0].split(" ")) > maxLength:
            return [sentences[0]] + combine_sentences(sentences[1:], maxLength=maxLength)

        if len((sentences[0] + sentences[1]).split(" ")) <= maxLength:
            return combine_sentences([sentences[0] + " " + sentences[1]]+sentences[2:], maxLength=maxLength)
        else:
            return [sentences[0]] + combine_sentences(sentences[1:], maxLength=maxLength)

def split_long_sentences(sentences: list, maxLength: int = 30) -> list:
    sub_sentences = []
    for sentence in sentences:
        if len(sentence.split(" ")) > maxLength:
            sub_sentences.append(split_text_sentences(sentence,  r'[?!.,:;-]'))
        else:
            sub_sentences.append([sentence])
    return sub_sentences
    
def get_pieces(passage: str, maxLength: int):
    sub_sentences = split_long_sentences(split_text_sentences(passage, r'[.!?]'), maxLength)
    combined_sub_sentences = [combine_sentences(
        i, maxLength) for i in sub_sentences]
    flat_list = []
    for sublist in combined_sub_sentences:
        for item in sublist:
            item_chars = set([i for i in item])
            if not punctuations.issuperset(item_chars) and any(map(isTextOnly, item_chars)):
                flat_list.append(item)
    return flat_list