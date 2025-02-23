import re
from jamo import h2j, j2h
import os

############## English ##############
def adjust(arpabets):
    '''Modify arpabets so that it fits our processes'''
    string = " " + " ".join(arpabets) + " $"
    string = re.sub("\d", "", string)
    string = string.replace(" T S ", " TS ")
    string = string.replace(" D Z ", " DZ ")
    string = string.replace(" AW ER ", " AWER ")
    string = string.replace(" IH R $", " IH ER ")
    string = string.replace(" EH R $", " EH ER ")
    string = string.replace(" $", "")

    return string.strip("$ ").split()


def to_choseong(arpabet):
    '''Arpabet to choseong or onset'''
    d = \
        {'B': 'ᄇ',
         'CH': 'ᄎ',
         'D': 'ᄃ',
         'DH': 'ᄃ',
         'DZ': 'ᄌ',
         'F': 'ᄑ',
         'G': 'ᄀ',
         'HH': 'ᄒ',
         'JH': 'ᄌ',
         'K': 'ᄏ',
         'L': 'ᄅ',
         'M': 'ᄆ',
         'N': 'ᄂ',
         'NG': 'ᄋ',
         'P': 'ᄑ',
         'R': 'ᄅ',
         'S': 'ᄉ',
         'SH': 'ᄉ',
         'T': 'ᄐ',
         'TH': 'ᄉ',
         'TS': 'ᄎ',
         'V': 'ᄇ',
         'W': 'W',
         'Y': 'Y',
         'Z': 'ᄌ',
         'ZH': 'ᄌ'}

    return d.get(arpabet, arpabet)

def to_jungseong(arpabet):
    '''Arpabet to jungseong or vowel'''
    d = \
        {'AA': 'ᅡ',
         'AE': 'ᅢ',
         'AH': 'ᅥ',
         'AO': 'ᅩ',
         'AW': 'ᅡ우',
         'AWER': "ᅡ워",
         'AY': 'ᅡ이',
         'EH': 'ᅦ',
         'ER': 'ᅥ',
         'EY': 'ᅦ이',
         'IH': 'ᅵ',
         'IY': 'ᅵ',
         'OW': 'ᅩ',
         'OY': 'ᅩ이',
         'UH': 'ᅮ',
         'UW': 'ᅮ'}
    return d.get(arpabet, arpabet)

def to_jongseong(arpabet):
    '''Arpabet to jongseong or coda'''
    d = \
        {'B': 'ᆸ',
         'CH': 'ᆾ',
         'D': 'ᆮ',
         'DH': 'ᆮ',
         'F': 'ᇁ',
         'G': 'ᆨ',
         'HH': 'ᇂ',
         'JH': 'ᆽ',
         'K': 'ᆨ',
         'L': 'ᆯ',
         'M': 'ᆷ',
         'N': 'ᆫ',
         'NG': 'ᆼ',
         'P': 'ᆸ',
         'R': 'ᆯ',
         'S': 'ᆺ',
         'SH': 'ᆺ',
         'T': 'ᆺ',
         'TH': 'ᆺ',
         'V': 'ᆸ',
         'W': 'ᆼ',
         'Y': 'ᆼ',
         'Z': 'ᆽ',
         'ZH': 'ᆽ'}

    return d.get(arpabet, arpabet)


def reconstruct(string):
    '''Some postprocessing rules'''
    pairs = [("그W", "ᄀW"),
             ("흐W", "ᄒW"),
             ("크W", "ᄏW"),
             ("ᄂYᅥ", "니어"),
             ("ᄃYᅥ", "디어"),
             ("ᄅYᅥ", "리어"),
             ("Yᅵ", "ᅵ"),
             ("Yᅡ", "ᅣ"),
             ("Yᅢ", "ᅤ"),
             ("Yᅥ", "ᅧ"),
             ("Yᅦ", "ᅨ"),
             ("Yᅩ", "ᅭ"),
             ("Yᅮ", "ᅲ"),
             ("Wᅡ", "ᅪ"),
             ("Wᅢ", "ᅫ"),
             ("Wᅥ", "ᅯ"),
             ("Wᅩ", "ᅯ"),
             ("Wᅮ", "ᅮ"),
             ("Wᅦ", "ᅰ"),
             ("Wᅵ", "ᅱ"),
             ("ᅳᅵ", "ᅴ"),
             ("Y", "ᅵ"),
             ("W", "ᅮ")
             ]
    for str1, str2 in pairs:
        string = string.replace(str1, str2)
    return string


############## Hangul ##############
def parse_table():
    '''Parse the main rule table'''
    lines = open(os.path.dirname(os.path.abspath(__file__)) + '/table.csv', 'r', encoding='utf8').read().splitlines()
    onsets = lines[0].split(",")
    table = []
    for line in lines[1:]:
        cols = line.split(",")
        coda = cols[0]
        for i, onset in enumerate(onsets):
            cell = cols[i]
            if len(cell)==0: continue
            if i==0:
                continue
            else:
                str1 = f"{coda}{onset}"
                if "(" in cell:
                    str2 = cell.split("(")[0]
                    rule_ids = cell.split("(")[1][:-1].split("/")
                else:
                    str2 = cell
                    rule_ids = []

                table.append((str1, str2, rule_ids))
    return table


############## Preprocessing ##############
def annotate(string, mecab):
    '''attach pos tags to the given string using Mecab
    mecab: mecab object
    '''
    if os.name == 'nt':
        parse = mecab.parse(string).split('\n')
        tokens = []
        for p in parse[:-2]:
            p1, p2 = p.split('\t')
            p2 = p2.split(',')[0]
            tokens.append((p1, p2))
    elif os.name == 'posix':
        tokens = mecab.pos(string)
    
    if re.sub(r'[ \n]', '', string) != "".join(token for token, _ in tokens):
        return string
    blanks = [(i, char) for i, char in enumerate(string) if char in (" ", "\n")]

    tag_seq = []
    for token, tag in tokens:
        tag = tag.split("+")[-1]
        if tag=="NNBC" or token=='곳': # bound noun
            tag = "B"
        else:
            tag = tag[0]
        tag_seq.append("_" * (len(token) - 1) + tag)
    tag_seq = "".join(tag_seq)

    for i, char in blanks:
        tag_seq = tag_seq[:i] + char + tag_seq[i:]

    annotated = ""
    for char, tag in zip(string, tag_seq):
        annotated += char
        if char == "의" and tag == "J":
            annotated += "/J"
        elif tag=="E":
            if h2j(char)[-1] in "ᆯ":
                annotated += "/E"
        elif tag == "V":
            if h2j(char)[-1] in "ᆫᆬᆷᆱᆰᆲᆴ":
                annotated += "/P"
        elif tag == "B": # bound noun
            annotated += "/B"

    return annotated


############## Postprocessing ##############
def compose(letters):
    # insert placeholder
    letters = re.sub("(^|[^\u1100-\u1112])([\u1161-\u1175])", r"\1ᄋ\2", letters)

    string = letters # assembled characters
    # c+v+c
    syls = set(re.findall("[\u1100-\u1112][\u1161-\u1175][\u11A8-\u11C2]", string))
    for syl in syls:
        string = string.replace(syl, j2h(*syl))

    # c+v
    syls = set(re.findall("[\u1100-\u1112][\u1161-\u1175]", string))
    for syl in syls:
        string = string.replace(syl, j2h(*syl))

    return string


def group(inp):
    '''For group_vowels=True
    Contemporarily, Korean speakers don't distinguish some vowels.
    '''
    inp = inp.replace("ᅢ", "ᅦ")
    inp = inp.replace("ᅤ", "ᅨ")
    inp = inp.replace("ᅫ", "ᅬ")
    inp = inp.replace("ᅰ", "ᅬ")

    return inp


def _get_examples():
    '''For internal use'''
    text = open('rules.txt', 'r', encoding='utf8').read().splitlines()
    examples = []
    for line in text:
        if line.startswith("->"):
            examples.extend(re.findall("([ㄱ-힣][ ㄱ-힣]*)\[([ㄱ-힣][ ㄱ-힣]*)]", line))
    _examples = []
    for inp, gt in examples:
        for each in gt.split("/"):
            _examples.append((inp, each))

    return _examples


############## Utilities ##############
def get_rule_id2text():
    '''for verbose=True'''
    rules = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules.txt'), 'r', encoding='utf8').read().strip().split("\n\n")
    rule_id2text = dict()
    for rule in rules:
        rule_id, texts = rule.splitlines()[0], rule.splitlines()[1:]
        rule_id2text[rule_id.strip()] = "\n".join(texts)
    return rule_id2text


def gloss(verbose, out, inp, rule):
    '''displays the process and relevant information'''
    if verbose and out != inp and out != re.sub("/[EJPB]", "", inp):
        print(compose(inp), "->", compose(out))
        print("\033[1;31m", rule, "\033[0m")




