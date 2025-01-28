import re
from string import punctuation
from .en import G2P
from underthesea.pipeline.word_tokenize import tokenize, regex_tokenize
import re
from .num2vi import n2w, n2w_single
from collections import deque
from . import data
import importlib.resources
import json
from dataclasses import dataclass

# import prosodic as p
#  (C1)(w)V(G|C2)+T

#symbol " ' " for undefine symbol and sign for english

'''
C1 = initial consonant onset
w = labiovelar on-glide /w/
V = vowel nucleus
G = off-glide coda (/j/ or /w/)
C2 = final consonant coda
T = tone.
'''
Cus_onsets = { u'b' : u'b', u't' : u't', u'th' : u'tʰ', u'đ' : u'd', u'ch' : u'c', 
                u'kh' : u'x', u'g' : u'ɣ', u'l' : u'l', u'm' : u'm', u'n': u'n', 
                u'ngh': u'ŋ', u'nh' : u'ɲ', u'ng' : u'ŋ', u'ph' : u'f', u'v' : u'v', 
                u'x' : u's', u'd' : u'z', u'h' : u'h', u'p' : u'p', u'qu' : u'kw',
                u'gi' : u'j', u'tr' : u'ʈ', u'k' : u'k', u'c' : u'k', u'gh' : u'ɣ', 
                u'r' : u'ʐ', u's' : u'ʂ', u'gi': u'j'}

# Old or mixed alphabet
Cus_onsets.update({'f': 'f', 'j': 'j', 'w': 'w', 'z': 'z'})
              
Cus_nuclei = { u'a' : u'a', u'á' : u'a', u'à' : u'a', u'ả' : u'a', u'ã' : u'a', u'ạ' : u'a', 
                u'â' : u'ɤ̆', u'ấ' : u'ɤ̆', u'ầ' : u'ɤ̆', u'ẩ' : u'ɤ̆', u'ẫ' : u'ɤ̆', u'ậ' : u'ɤ̆',
                u'ă' : u'ă', u'ắ' : u'ă', u'ằ' : u'ă', u'ẳ' : u'ă', u'ẵ' : u'ă', u'ặ' : u'ă',
                u'e' : u'ɛ', u'é' : u'ɛ', u'è' : u'ɛ', u'ẻ' : u'ɛ', u'ẽ' : u'ɛ', u'ẹ' : u'ɛ',
                u'ê' : u'e', u'ế' : u'e', u'ề' : u'e', u'ể' : u'e', u'ễ' : u'e', u'ệ' : u'e',
                u'i' : u'i', u'í' : u'i', u'ì' : u'i', u'ỉ' : u'i', u'ĩ' : u'i', u'ị' : u'i',
                u'o' : u'ɔ', u'ó' : u'ɔ', u'ò' : u'ɔ', u'ỏ' : u'ɔ', u'õ' : u'ɔ', u'ọ' : u'ɔ',
                u'ô' : u'o', u'ố' : u'o', u'ồ' : u'o', u'ổ' : u'o', u'ỗ' : u'o', u'ộ' : u'o',
                u'ơ' : u'ɤ', u'ớ' : u'ɤ', u'ờ' : u'ɤ', u'ở' : u'ɤ', u'ỡ' : u'ɤ', u'ợ' : u'ɤ',
                u'u' : u'u', u'ú' : u'u', u'ù' : u'u', u'ủ' : u'u', u'ũ' : u'u', u'ụ' : u'u',
                u'ư' : u'ɯ', u'ứ' : u'ɯ', u'ừ' : u'ɯ', u'ử' : u'ɯ', u'ữ' : u'ɯ', u'ự' : u'ɯ',
                u'y' : u'i', u'ý' : u'i', u'ỳ' : u'i', u'ỷ' : u'i', u'ỹ' : u'i', u'ỵ' : u'i',
                
                u'eo' : u'eo', u'éo' : u'eo', u'èo' : u'eo', u'ẻo' : u'eo', u'ẽo': u'eo', u'ẹo' : u'eo',
                u'êu' : u'ɛu', u'ếu' : u'ɛu', u'ều' : u'ɛu', u'ểu' : u'ɛu', u'ễu': u'ɛu', u'ệu' : u'ɛu',
                u'ia' : u'iə', u'ía' : u'iə', u'ìa' : u'iə', u'ỉa' : u'iə', u'ĩa' : u'iə', u'ịa' : u'iə',
                u'ia' : u'iə', u'iá' : u'iə', u'ià' : u'iə', u'iả' : u'iə', u'iã' : u'iə', u'iạ' : u'iə',
                u'iê' : u'iə', u'iế' : u'iə', u'iề' : u'iə', u'iể' : u'iə', u'iễ' : u'iə', u'iệ' : u'iə',
                u'oo' : u'ɔ', u'óo' : u'ɔ', u'òo' : u'ɔ', u'ỏo' : u'ɔ', u'õo' : u'ɔ', u'ọo' : u'ɔ',
                u'oo' : u'ɔ', u'oó' : u'ɔ', u'oò' : u'ɔ', u'oỏ' : u'ɔ', u'oõ' : u'ɔ', u'oọ' : u'ɔ',
                u'ôô' : u'o', u'ốô' : u'o', u'ồô' : u'o', u'ổô' : u'o', u'ỗô' : u'o', u'ộô' : u'o',                                 
                u'ôô' : u'o', u'ôố' : u'o', u'ôồ' : u'o', u'ôổ' : u'o', u'ôỗ' : u'o', u'ôộ' : u'o',                                  
                u'ua' : u'uə', u'úa' : u'uə', u'ùa' : u'uə', u'ủa' : u'uə', u'ũa' : u'uə', u'ụa' : u'uə',
                u'uô' : u'uə', u'uố' : u'uə', u'uồ' : u'uə', u'uổ' : u'uə', u'uỗ' : u'uə', u'uộ' : u'uə',
                u'ưa' : u'ɯə', u'ứa' : u'ɯə', u'ừa' : u'ɯə', u'ửa' : u'ɯə', u'ữa' : u'ɯə', u'ựa' : u'ɯə',
                u'ươ' : u'ɯə', u'ướ' : u'ɯə', u'ườ' : u'ɯə', u'ưở' : u'ɯə', u'ưỡ' : u'ɯə', u'ượ' : u'ɯə',
                u'yê' : u'iɛ', u'yế' : u'iɛ', u'yề' : u'iɛ', u'yể' : u'iɛ', u'yễ' : u'iɛ', u'yệ' : u'iɛ', 
                u'uơ' : u'uə',  u'uở' : u'uə', u'uờ': u'uə', u'uở' : u'uə', u'uỡ' : u'uə', u'uợ' : u'uə',
                }
                         
             
Cus_offglides = { u'ai' : u'aj', u'ái' : u'aj', u'ài' : u'aj', u'ải' : u'aj', u'ãi' : u'aj', u'ại' : u'aj',
                  u'ay' : u'ăj', u'áy' : u'ăj', u'ày' : u'ăj', u'ảy' : u'ăj', u'ãy' : u'ăj', u'ạy' : u'ăj',
                  u'ao' : u'aw', u'áo' : u'aw', u'ào' : u'aw', u'ảo' : u'aw', u'ão' : u'aw', u'ạo' : u'aw',
                  u'au' : u'ăw', u'áu' : u'ăw', u'àu' : u'ăw', u'ảu' : u'ăw', u'ãu' : u'ăw', u'ạu' : u'ăw',
                  u'ây' : u'ɤ̆j',  u'ấy' : u'ɤ̆j',  u'ầy' : u'ɤ̆j', u'ẩy' : u'ɤ̆j', u'ẫy' : u'ɤ̆j', u'ậy' : u'ɤ̆j', 
                  u'âu' : u'ɤ̆w', u'ấu' : u'ɤ̆w', u'ầu': u'ɤ̆w', u'ẩu' : u'ɤ̆w', u'ẫu' : u'ɤ̆w', u'ậu' : u'ɤ̆w',
                  u'eo' : u'ew', u'éo' : u'ew', u'èo' : u'ew', u'ẻo' : u'ew', u'ẽo' : u'ew', u'ẹo' : u'ew',
                  u'iu' : u'iw', u'íu' : u'iw', u'ìu' : u'iw', u'ỉu' : u'iw', u'ĩu' : u'iw', u'ịu' : u'iw',
                  u'oi' : u'ɔj', u'ói' : u'ɔj', u'òi' : u'ɔj', u'ỏi' : u'ɔj', u'õi' : u'ɔj', u'ọi' : u'ɔj',
                  u'ôi' : u'oj', u'ối' : u'oj', u'ồi' : u'oj', u'ổi' : u'oj', u'ỗi' : u'oj', u'ội' : u'oj',
                  u'ui' : u'uj', u'úi' : u'uj', u'ùi' : u'uj', u'ủi' : u'uj', u'ũi' : u'uj', u'ụi' : u'uj', 
                  
                  #u'uy' : u'uj', u'úy' : u'uj', u'ùy' : u'uj', u'ủy' : u'uj', u'ũy' : u'uj', u'ụy' : u'uj', 
                  u'uy' : u'ʷi', u'úy' : u'uj', u'ùy' : u'uj', u'ủy' : u'uj', u'ũy' : u'uj', u'ụy' : u'uj',
                  # prevent duplicated phonemes
                  u'uy' : u'ʷi', u'uý' : u'ʷi', u'uỳ' : u'ʷi', u'uỷ' : u'ʷi', u'uỹ' : u'ʷi', u'uỵ' : u'ʷi',
                  
                  u'ơi' : u'ɤj', u'ới' : u'ɤj', u'ời' : u'ɤj', u'ởi' : u'ɤj', u'ỡi' : u'ɤj', u'ợi' : u'ɤj', 
                  u'ưi' : u'ɯj', u'ứi' : u'ɯj', u'ừi' : u'ɯj', u'ửi' : u'ɯj', u'ữi' : u'ɯj', u'ựi' : u'ɯj', 
                  u'ưu' : u'ɯw', u'ứu' : u'ɯw', u'ừu' : u'ɯw', u'ửu' : u'ɯw', u'ữu' : u'ɯw', u'ựu' : u'ɯw',

                  u'iêu' : u'iəw', u'iếu' : u'iəw', u'iều' : u'iəw', u'iểu' : u'iəw', u'iễu' : u'iəw', u'iệu' : u'iəw',
                  u'yêu' : u'iəw', u'yếu' : u'iəw', u'yều' : u'iəw', u'yểu' : u'iəw', u'yễu' : u'iəw', u'yệu' : u'iəw', 
                  u'uôi' : u'uəj', u'uối' : u'uəj', u'uồi' : u'uəj', u'uổi' : u'uəj', u'uỗi' : u'uəj', u'uội' : u'uəj', 
                  u'ươi' : u'ɯəj', u'ưới' : u'ɯəj', u'ười' : u'ɯəj', u'ưởi' : u'ɯəj', u'ưỡi' : u'ɯəj', u'ượi' : u'ɯəj', 
                  u'ươu' : u'ɯəw', u'ướu' : u'ɯəw', u'ườu' : u'ɯəw', u'ưởu' : u'ɯəw', 'ưỡu' : u'ɯəw', u'ượu' : u'ɯəw'     
                }
# The rounded vowels here are exactly not rounded: no w before => Try to add ʷ    
Cus_onglides = { u'oa' : u'ʷa', u'oá' : u'ʷa', u'oà' : u'ʷa', u'oả' : u'ʷa', u'oã' : u'ʷa', u'oạ' : u'ʷa', 
                      u'óa' : u'ʷa', u'òa' : u'ʷa', u'ỏa' : u'ʷa', u'õa' : u'ʷa', u'ọa' : u'ʷa', 
                  u'oă' : u'ʷă', u'oắ' : u'ʷă', u'oằ' : u'ʷă', u'oẳ' : u'ʷă', u'oẵ' : u'ʷă', u'oặ' : u'ʷă',     
                  u'oe' : u'ʷɛ', u'oé' : u'ʷɛ', u'oè' : u'ʷɛ', u'oẻ' : u'ʷɛ', u'oẽ' : u'ʷɛ', u'oẹ' : u'ʷɛ',     
                  u'oe' : u'ʷɛ', u'óe' : u'ʷɛ', u'òe' : u'ʷɛ', u'ỏe' : u'ʷɛ', u'õe' : u'ʷɛ', u'ọe' : u'ʷɛ',     
                  u'ua' : u'ʷa', u'uá' : u'ʷa', u'uà' : u'ʷa', u'uả' : u'ʷa', u'uã' : u'ʷa', u'uạ' : u'ʷa', 
                  u'uă' : u'ʷă', u'uắ' : u'ʷă', u'uằ' : u'ʷă', u'uẳ' : u'ʷă', u'uẵ' : u'ʷă', u'uặ' : u'ʷă',     
                  u'uâ' : u'ʷɤ̆', u'uấ' : u'ʷɤ̆', u'uầ' : u'ʷɤ̆', u'uẩ' : u'ʷɤ̆', u'uẫ' : u'ʷɤ̆', u'uậ' : u'ʷɤ̆', 
                  u'ue' : u'ʷɛ', u'ué' : u'ʷɛ', u'uè' : u'ʷɛ', u'uẻ' : u'ʷɛ', u'uẽ' : u'ʷɛ', u'uẹ' : u'ʷɛ', 
                  u'uê' : u'ʷe', u'uế' : u'ʷe', u'uề' : u'ʷe', u'uể' : u'ʷe', u'uễ' : u'ʷe', u'uệ' : u'ʷe', 
                  u'uơ' : u'ʷɤ', u'uớ' : u'ʷɤ', u'uờ' : u'ʷɤ', u'uở' : u'ʷɤ', u'uỡ' : u'ʷɤ', u'uợ' : u'ʷɤ', 
                  u'uy' : u'ʷi', u'uý' : u'ʷi', u'uỳ' : u'ʷi', u'uỷ' : u'ʷi', u'uỹ' : u'ʷi', u'uỵ' : u'ʷi',
                  u'uya' : u'ʷiə', u'uyá' : u'ʷiə', u'uyà' : u'ʷiə', u'uyả' : u'ʷiə', u'uyã' : u'ʷiə', u'uyạ' : u'ʷiə', 
                  u'uyê' : u'ʷiə', u'uyế' : u'ʷiə', u'uyề' : u'ʷiə', u'uyể' : u'ʷiə', u'uyễ' : u'ʷiə', u'uyệ' : u'ʷiə', 
                  u'uyu' : u'ʷiu', u'uyú' : u'ʷiu', u'uyù' : u'ʷiu', u'uyủ' : u'ʷiu', u'uyũ' : u'ʷiu', u'uyụ' : u'ʷiu', 
                  u'uyu' : u'ʷiu', u'uýu' : u'ʷiu', u'uỳu' : u'ʷiu', u'uỷu' : u'ʷiu', u'uỹu' : u'ʷiu', u'uỵu' : u'ʷiu',
                  u'oen' : u'ʷen', u'oén' : u'ʷen', u'oèn' : u'ʷen', u'oẻn' : u'ʷen', u'oẽn' : u'ʷen', u'oẹn' : u'ʷen',     
                  u'oet' : u'ʷet', u'oét' : u'ʷet', u'oèt' : u'ʷet', u'oẻt' : u'ʷet', u'oẽt' : u'ʷet', u'oẹt' : u'ʷet'     
                }

Cus_onoffglides = { u'oe' : u'ɛj', u'oé' : u'ɛj', u'oè' : u'ɛj', u'oẻ' : u'ɛj', u'oẽ' : u'ɛj', u'oẹ' : u'ɛj', 
                   u'oai' : u'aj', u'oái' : u'aj', u'oài' : u'aj', u'oải' : u'aj', u'oãi' : u'aj', u'oại' : u'aj',
                   u'oay' : u'ăj', u'oáy' : u'ăj', u'oày' : u'ăj', u'oảy' : u'ăj', u'oãy' : u'ăj', u'oạy' : u'ăj',
                   u'oao' : u'aw', u'oáo' : u'aw', u'oào' : u'aw', u'oảo' : u'aw', u'oão' : u'aw', u'oạo' : u'aw',
                   u'oeo' : u'ew', u'oéo' : u'ew', u'oèo' : u'ew', u'oẻo' : u'ew', u'oẽo' : u'ew', u'oẹo' : u'ew',
                   u'oeo' : u'ew', u'óeo' : u'ew', u'òeo' : u'ew', u'ỏeo' : u'ew', u'õeo' : u'ew', u'ọeo' : u'ew',
                   u'ueo' : u'ew', u'uéo' : u'ew', u'uèo' : u'ew', u'uẻo' : u'ew', u'uẽo' : u'ew', u'uẹo' : u'ew',
                   u'uai' : u'aj', u'uái' : u'aj', u'uài' : u'aj', u'uải' : u'aj', u'uãi' : u'aj', u'uại' : u'aj',
                   u'uay' : u'ăj', u'uáy' : u'ăj', u'uày' : u'ăj', u'uảy' : u'ăj', u'uãy' : u'ăj', u'uạy' : u'ăj',
                   u'uây' : u'ɤ̆j', u'uấy' : u'ɤ̆j', u'uầy' : u'ɤ̆j', u'uẩy' : u'ɤ̆j', u'uẫy' : u'ɤ̆j', u'uậy' : u'ɤ̆j'
                 }

Cus_codas = { u'p' : u'p', u't' : u't', u'c' : u'k', u'm' : u'm', u'n' : u'n', u'ng' : u'ŋ', u'nh' : u'ɲ', u'ch' : u'tʃ', u'k': 'k' }

Cus_tones_p = { u'á' : 5, u'à' : 2, u'ả' : 4, u'ã' : 3, u'ạ' : 6, 
                u'ấ' : 5, u'ầ' : 2, u'ẩ' : 4, u'ẫ' : 3, u'ậ' : 6,
                u'ắ' : 5, u'ằ' : 2, u'ẳ' : 4, u'ẵ' : 3, u'ặ' : 6,
                u'é' : 5, u'è' : 2, u'ẻ' : 4, u'ẽ' : 3, u'ẹ' : 6,
                u'ế' : 5, u'ề' : 2, u'ể' : 4, u'ễ' : 3, u'ệ' : 6,
                u'í' : 5, u'ì' : 2, u'ỉ' : 4, u'ĩ' : 3, u'ị' : 6,
                u'ó' : 5, u'ò' : 2, u'ỏ' : 4, u'õ' : 3, u'ọ' : 6,
                u'ố' : 5, u'ồ' : 2, u'ổ' : 4, u'ỗ' : 3, u'ộ' : 6,
                u'ớ' : 5, u'ờ' : 2, u'ở' : 4, u'ỡ' : 3, u'ợ' : 6,
                u'ú' : 5, u'ù' : 2, u'ủ' : 4, u'ũ' : 3, u'ụ' : 6,
                u'ứ' : 5, u'ừ' : 2, u'ử' : 4, u'ữ' : 3, u'ự' : 6,
                u'ý' : 5, u'ỳ' : 2, u'ỷ' : 4, u'ỹ' : 3, u'ỵ' : 6,
              }
              
Cus_gi = { u'gi' : u'zi', u'gí': u'zi', u'gì' : u'zi', u'gì' : u'zi', u'gĩ' : u'zi', u'gị' : u'zi'}

Cus_qu = {u'quy' : u'kwi', u'qúy' : u'kwi', u'qùy' : u'kwi', u'qủy' : u'kwi', u'qũy' : u'kwi', u'qụy' : u'kwi'}

# letter pronunciation
EN = {"a":"ây","b":"bi","c":"si","d":"đi","e":"i","f":"ép","g":"giy","h":"hếch","i":"ai","j":"giây","k":"cây","l":"eo","m":"em","n":"en","o":"âu","p":"pi","q":"kiu","r":"a","s":"ét","t":"ti","u":"diu","ư":"ư","v":"vi","w":"đắp liu","x":"ít","y":"quai","z":"giét"}
VI = {"a":"a","ă":"á","â":"ớ","b":"bê","c":"cê","d":"dê","đ":"đê","e":"e","ê":"ê","f":"phờ","g":"gờ","h":"hờ","i":"i","j":"giây","k":"ka","l":"lờ","m":"mờ","n":"nờ","o":"o","ô":"ô","ơ":"ơ","p":"pờ","q":"quy","r":"rờ","s":"sờ","t":"tờ","u":"u","ư":"ư","v":"vi","w":"gờ","x":"xờ","y":"i","z":"gia"}
vi_syms = ['ɯəj', 'ɤ̆j', 'ʷiə', 'ɤ̆w', 'ɯəw', 'ʷet', 'iəw', 'uəj', 'ʷen', 'tʰw', 'ʷɤ̆', 'ʷiu', 'kwi', 'ŋ͡m', 'k͡p', 'cw', 'jw', 'uə', 'eə', 'bw', 'oj', 'ʷi', 'vw', 'ăw', 'ʈw', 'ʂw', 'aʊ', 'fw', 'ɛu', 'tʰ', 'tʃ', 'ɔɪ', 'xw', 'ʷɤ', 'ɤ̆', 'ŋw', 'ʊə', 'zi', 'ʷă', 'dw', 'eɪ', 'aɪ', 'ew', 'iə', 'ɣw', 'zw', 'ɯj', 'ʷɛ', 'ɯw', 'ɤj', 'ɔ:', 'əʊ', 'ʷa', 'mw', 'ɑ:', 'hw', 'ɔj', 'uj', 'lw', 'ɪə', 'ăj', 'u:', 'aw', 'ɛj', 'iw', 'aj', 'ɜ:', 'kw', 'nw', 't∫', 'ɲw', 'eo', 'sw', 'tw', 'ʐw', 'iɛ', 'ʷe', 'i:', 'ɯə', 'dʒ', 'ɲ', 'θ', 'ʌ', 'l', 'w', '1', 'ɪ', 'ɯ', 'd', '∫', 'p', 'ə', 'u', 'o', '3', 'ɣ', '!', 'ð', 'ʧ', '6', 'ʒ', 'ʐ', 'z', 'v', 'g', 'ă', 'æ', 'ɤ', '2', 'ʤ', 'i', '.', 'ɒ', 'b', 'h', 'n', 'ʂ', 'ɔ', 'ɛ', 'k', 'm', '5', ' ', 'c', 'j', 'x', 'ʈ', ',', '4', 'ʊ', 's', 'ŋ', 'a', 'ʃ', '?', 'r', ':', 'η', 'f', ';', 'e', 't', "'"]

with importlib.resources.open_text(data, 'vi_symbols.json', encoding = "utf-8") as r:
    SYMBOL_MAPPING = json.load(r)
with importlib.resources.open_text(data, 'vi_teencode.json', encoding = "utf-8") as r:
    TEENCODE_MAPPING = json.load(r)
NUMBER_REGEX = re.compile(regex_tokenize.number)
SYMBOL_REGEX = re.compile('|'.join(re.escape(symbol) for symbol in SYMBOL_MAPPING.keys()))
EN_VI_REGEX = re.compile("^[!-~“”–" + regex_tokenize.VIETNAMESE_CHARACTERS_LOWER + "]+$", re.IGNORECASE)
VI_ONLY = re.compile('|'.join(re.escape(c) for c in regex_tokenize.VIETNAMESE_CHARACTERS_LOWER if not c.isascii()), re.IGNORECASE)

################################################3

def trans(word, dialect, glottal, pham, cao, palatals):
    #Custom
    onsets, nuclei, codas, onglides, offglides, onoffglides, qu, gi = Cus_onsets, Cus_nuclei, Cus_codas,  Cus_onglides, Cus_offglides, Cus_onoffglides, Cus_qu, Cus_gi
    if pham or cao:
        #Custom
        tones_p = Cus_tones_p
        tones = tones_p

    ons = ''
    nuc = ''
    cod = ''
    ton = 0
    oOffset = 0
    cOffset = 0 
    l = len(word)

    if l > 0:
        if word[0:3] in onsets:         # if onset is 'ngh'
            ons = onsets[word[0:3]]
            oOffset = 3
        elif word[0:2] in onsets:       # if onset is 'nh', 'gh', 'kʷ' etc
            ons = onsets[word[0:2]]
            oOffset = 2
        elif word[0] in onsets:         # if single onset
            ons = onsets[word[0]]
            oOffset = 1

        if word[l-2:l] in codas:        # if two-character coda
            cod = codas[word[l-2:l]]
            cOffset = 2
        elif word[l-1] in codas:        # if one-character coda
            cod = codas[word[l-1]]
            cOffset = 1
                            

        #if word[0:2] == u'gi' and cod and len(word) == 3:  # if you just have 'gi' and a coda...
        if word[0:2] in gi and cod and len(word) == 3:  # if you just have 'gi' and a coda...
            nucl = u'i'
            ons = u'z'
        else:
            nucl = word[oOffset:l-cOffset]

        if nucl in nuclei:
            if oOffset == 0:
                if glottal == 1:
                    if word[0] not in onsets:   # if there isn't an onset....  
                        ons = u'ʔ'+nuclei[nucl] # add a glottal stop
                    else:                       # otherwise...
                        nuc = nuclei[nucl]      # there's your nucleus 
                else: 
                    nuc = nuclei[nucl]          # there's your nucleus 
            else:                               # otherwise...
                nuc = nuclei[nucl]              # there's your nucleus
        
        elif nucl in onglides and ons != u'kw': # if there is an onglide...
            nuc = onglides[nucl]                # modify the nuc accordingly
            if ons:                             # if there is an onset...
                ons = ons + u'w'                  # labialize it, but...
            else:                               # if there is no onset...
                ons = u'w'                      # add a labiovelar onset 

        elif nucl in onglides and ons == u'kw': 
            nuc = onglides[nucl]
                
        elif nucl in onoffglides:
            cod = onoffglides[nucl][-1]
            nuc = onoffglides[nucl][0:-1]
            if ons != u'kw':
                if ons:
                    ons = ons + u'w'
                else:
                    ons = u'w'
        elif nucl in offglides:
            cod = offglides[nucl][-1]
            nuc = offglides[nucl][:-1]
                
        elif word in gi:      # if word == 'gi', 'gì',...
            ons = gi[word][0]
            nuc = gi[word][1]

        elif word in qu:      # if word == 'quy', 'qúy',...
            ons = qu[word][:-1]
            nuc = qu[word][-1]
                
        else:   
            # Something is non-Viet
            return (None, None, None, None)


        # Velar Fronting (Northern dialect)
        if dialect == 'n':
            if nuc == u'a':
                if cod == u'k' and cOffset == 2: nuc = u'ɛ'
                if cod == u'ɲ' and nuc == u'a': nuc = u'ɛ'

            # Final palatals (Northern dialect)
            if nuc not in [u'i', u'e', u'ɛ']:
                if cod == u'ɲ': 
                    cod = u'ɲ' # u'ŋ'
            elif palatals != 1 and nuc in [u'i', u'e', u'ɛ']:
                if cod == u'ɲ': 
                    cod = u'ɲ'#u'ŋ'
            if palatals == 1:
                if cod == u'k' and nuc in [u'i', u'e', u'ɛ']: 
                    cod = u'c'

        # Velar Fronting (Southern and Central dialects)
        else:
            if nuc in [u'i', u'e']:
                if cod == u'k': cod = u't'
                if cod == u'ŋ': cod = u'n'

            # There is also this reverse fronting, see Thompson 1965:94 ff.
            elif nuc in [u'iə', u'ɯə', u'uə', u'u', u'ɯ', u'ɤ', u'o', u'ɔ', u'ă', u'ɤ̆']:
                if cod == u't': 
                    cod = u'k'
                if cod == u'n': cod = u'ŋ'

        # Monophthongization (Southern dialects: Thompson 1965: 86; Hoàng 1985: 181)
        if dialect == 's':
            if cod in [u'm', u'p']:
                if nuc == u'iə': nuc = u'i'
                if nuc == u'uə': nuc = u'u'
                if nuc == u'ɯə': nuc = u'ɯ'

        # Tones 
        # Modified 20 Sep 2008 to fix aberrant 33 error
        tonelist = [tones[word[i]] for i in range(0,l) if word[i] in tones]
        if tonelist:
            ton = str(tonelist[len(tonelist)-1])
        else:
            if not (pham or cao):
                if dialect == 'c':
                    ton = str('35')
                else:
                    ton = str('33')
            else:
                ton = str('1')
            
        # Modifications for closed syllables
        if cOffset !=0:

            # Obstruent-final nang tones are modal voice
            if (dialect == 'n' or dialect == 's') and ton == u'21g' and cod in ['p', 't', 'k']:
                #if ton == u'21\u02C0' and cod in ['p', 't', 'k']: # fixed 8 Nov 2016
                ton = u'21'

            # Modification for sắc in closed syllables (Northern and Central only)
            if ((dialect == 'n' and ton == u'24') or (dialect == 'c' and ton == u'13')) and cod in ['p', 't', 'k']:
                ton = u'45'

            # Modification for 8-tone system
            if cao == 1:
                if ton == u'5' and cod in ['p', 't', 'k']:
                    ton = u'5b'
                if ton == u'6' and cod in ['p', 't', 'k']:
                    ton = u'6b'

            # labialized allophony (added 17.09.08)
            if nuc in [u'u', u'o', u'ɔ']:
                if cod == u'ŋ':
                    cod = u'ŋ͡m' 
                if cod == u'k':
                    cod = u'k͡p'

        return (ons, nuc, cod, ton)
    
def convert(word, dialect, glottal, pham, cao, palatals, delimit):
    """Convert a single orthographic string to IPA."""

    ons = ''
    nuc = ''
    cod = ''
    ton = 0
    seq = ''

    try:
        (ons, nuc, cod, ton) = trans(word, dialect, glottal, pham, cao, palatals)
        if None in (ons, nuc, cod, ton):
            seq = u'['+word+u']'
        else:
            seq = delimit + delimit.join(filter(None, (ons, nuc, cod, ton)))+delimit
    except (TypeError):
        pass

    return seq

########################333

def Parsing(listParse, text, delimit):
    undefine_symbol = "'"
    if listParse == "default":
        listParse = vi_syms.copy()
    listParse.sort(reverse = True,key = len)
    output = ""
    skip = 0
    for ic,char in enumerate(text):
        ##print(char,skip)
        check = 0
        if skip>0:
            skip = skip-1
            continue
        for l in listParse:
            
            if len(l) <= len(text[ic:]) and l == text[ic:ic + len(l)]:
                output += delimit + l
                check =1
                skip = len(l)-1
                break
        if check == 0:
            #Case symbol not in list
            if str(char) in ["ˈ","ˌ","*"]:
                continue
            #print("this is not in symbol :"+ char + ":")
            output += delimit + undefine_symbol
    return output.rstrip()+delimit

# Pseudo implementation of vinorm
def TTSnorm(text, use_linking_words = True):
    def number_fn(match):
        number = ''.join([c for c in match.group('number') if c.isdigit()])
        if len(number) == 0:
            return ''
        if len(number) > 1:
            number = number.removeprefix('0')
        if use_linking_words:
            words = n2w(number)
        else:
            words = n2w_single(number)
        return words
    text = NUMBER_REGEX.sub(number_fn, text)
    return text

@dataclass
class ViToken:
    text: str
    phonemes: str = None
    parent: str = None

class VIG2P:
    def __init__(self, 
                 glottal = 0, pham = 0, cao = 0, palatals = 0, substr_tokenize = True, dialect = "north",
                 tone_type = 0, num2words_use_linking_words = True,
                 enable_en_g2p = True, en_g2p_kwargs = {}):
        self.glottal = glottal
        self.pham = pham
        self.cao = cao
        self.palatals = palatals
        self.substr_tokenize = substr_tokenize
        self.delimit = ''
        self.tone_type = tone_type
        self.num2words_use_linking_words = num2words_use_linking_words
        if dialect in ["north", "central", "south"]:
            self.dialect = dialect[0]
        else:
            raise NotImplementedError(f"Vietnamese dialect {dialect}")
        if self.tone_type==0:
            self.pham = 1
        else:
            self.cao = 1
        en_g2p_kwargs["unk"] = '❓'
        self.en_g2p = G2P(**en_g2p_kwargs) if enable_en_g2p else lambda _: ('❓', [])
    
    def substr2ipa(self, tk, ipa):
        """
        Approximation of foreign name pronunciation
        Return (parent, text, phonemes)
        Example:
            Y:  /i/
            
            Blôk: 
            - k -> /k/
            - ôk -> /ok͡p1/
            - lôk -> /lok͡p1/
            - Blôk -> ❌
            - B -> Bờ -> bɤ2
            => /bɤ2 lok͡p1/
            
            Êban:
            - n -> /nɤ2/
            - an -> /an1/
            - ban -> /ban1/
            - Êban -> ❌
            - Ê -> /e1/
            => /e1 ban1/
        
        => /i bɤ2 lok͡p1 e1 ban1/
        """
        if '[' not in ipa:
            return [(None, tk, ipa)]

        if tk.lower().upper() == tk:
            # Handle acronym by letter-by-letter
            mapping = VI if VI_ONLY.search(tk) is not None else EN
            return [
                (tk, char, 
                 convert(mapping.get(char, char), self.dialect, self.glottal, self.pham, self.cao, self.palatals, ''))
                for char in tk.lower()
            ]
        
        orig_tk = tk
        tk = tk.lower()
        if VI_ONLY.search(tk) is None:
            eng, _ = self.en_g2p(tk)
            if '❓' not in eng:
                return [(None, tk, eng)]

        if not self.substr_tokenize:
            return [(None, tk, ipa)]

        parents = deque()
        parts = deque()
        sub_ipa = deque()
        while tk:
            if len(tk) == 1:
                char = tk
                _ipa = convert(
                    VI.get(char, char), self.dialect, self.glottal, self.pham, self.cao, self.palatals, ''
                )
                parents.appendleft(orig_tk)
                parts.appendleft(char)
                sub_ipa.appendleft(_ipa)
                break

            start, converted_ipa = -1, ''
            for i in range(len(tk) - 1, -1, -1):
                tkc = tk[i:]
                sub_tk = tkc if len(tkc) > 1 else VI.get(tkc, tkc)
                _ipa = convert(
                    sub_tk, self.dialect, self.glottal, self.pham, self.cao, self.palatals, ''
                )
                if '[' not in _ipa:
                    start = i
                    converted_ipa = _ipa

            if start != -1:
                parents.appendleft(orig_tk)
                sub_ipa.appendleft(converted_ipa)
                parts.appendleft(tk[start:])
                tk = tk[:start]
            else:
                break

        return list(zip(parents, parts, sub_ipa))

    def __call__(self, text):
        if self.substr_tokenize:
            text = text.replace('_', ' ').replace('-', ' ')
        TN = TTSnorm(text, self.num2words_use_linking_words)
        # Words in Vietnamese only have one morphological form, regardless of the compound words
        # so word segmentation is unnecessary
        # E.g. "nhà" trong "nhà xe" and "nhà lầu" are the same /ɲa2/
        TK = tokenize(TN)
        new_TK = []
        for word in TK:
            new_TK.extend(word.split())
        TK = new_TK
        IPA = ""
        vitokens: list[ViToken] = []
        for tk in TK:
            if EN_VI_REGEX.match(tk) is None:
                IPA += '['+tk+']' + " "
                vitokens.append(ViToken(tk, '['+tk+']'))
                continue
            if tk in ['.', ',', ';', ':', '!', '?', ')', '}', ']']:
                if tk in [')', '}', ']']:
                    tk = ')'
                IPA = IPA.rstrip() + tk + ' '
                vitokens.append(ViToken(tk))
                continue
            if tk in ['(', '{', '[']:
                tk = '('
                IPA += tk
                vitokens.append(ViToken(tk))
                continue
            if tk in ['"', "'", '–', '“', '”']:
                IPA += tk + ' '
                vitokens.append(ViToken(tk))
                continue
            tk = SYMBOL_REGEX.sub(lambda match: " " + SYMBOL_MAPPING[match[0]] + " ", tk)
            tk = TEENCODE_MAPPING.get(tk.lower(), tk)
            parent_tk_ipas = self.substr2ipa(tk, convert(tk.lower(), self.dialect, self.glottal, self.pham, self.cao, self.palatals, self.delimit))
            for parent, tk, ipa in parent_tk_ipas:
                IPA += ipa.strip() + " "
                vitokens.append(ViToken(tk, ipa, parent))
        return IPA.strip(), vitokens

__all__ = [VIG2P, vi_syms]
