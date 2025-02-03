# misaki/ko.py

from g2pk2 import G2p as BaseG2p
from .hangul.worker import convert
from .ko_convert import convert2
import re

class KOG2P:
    def __init__(self):
        self.g2p = BaseG2p()

    def __call__(self, text,version=2):
        text = self.g2p(text)
        self.version = version
        
        ps = ''
        for a, b in re.findall(r'([\uAC00-\uD7A3]+)|([^\uAC00-\uD7A3]+)', text):
            assert (not a) != (not b)
            if a:
                ps += convert2(a) if self.version == 2 else convert(a)
            else:
                ps += b
                if not b.endswith(' ') and not b.endswith(chr(8220)):
                    ps += ' '
        # ps = re.sub(r'(.)\*', r'\1\1', ps.strip()).replace('dʑ', 'ʥ').replace('tɕ', 'ʨ')
        return ps

# G2p를 KOG2P 클래스로 설정
G2p = KOG2P


##example
# from misaki import ko

# g2p = ko.G2p() # no transformer, American English

# text = '미사키는 코코로를 위해 만들어진 G2P 엔진입니다.'

# ps = g2p(text)

# print(ps) # 
