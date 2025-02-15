# COPIED from https://github.com/Greatdane/Convert-Numbers-to-Japanese/blob/master/Convert-Numbers-to-Japanese.py
# Japanese Number Converter
# - Currently using length functions - possible to use Recursive Functions? Difficult with the many exceptions
# - Works up to 9 figures (999999999)

romaji_dict = {".": "ten", "0": "zero", "1": "ichi", "2": "ni", "3": "san", "4": "yon", "5": "go", "6": "roku", "7": "nana",
                "8": "hachi", "9": "kyuu", "10": "juu", "100": "hyaku", "1000": "sen", "10000": "man", "100000000": "oku",
                "300": "sanbyaku", "600": "roppyaku", "800": "happyaku", "3000": "sanzen", "8000":"hassen", "01000": "issen"}

kanji_dict = {".": "点", "0": "零", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七",
                "8": "八", "9": "九", "10": "十", "100": "百", "1000": "千", "10000": "万", "100000000": "億",
              "300": "三百", "600": "六百", "800": "八百", "3000": "三千", "8000":"八千", "01000": "一千"}

hiragana_dict = {".": "てん", "0": "ゼロ", "1": "いち", "2": "に", "3": "さん", "4": "よん", "5": "ご", "6": "ろく", "7": "なな",
                "8": "はち", "9": "きゅう", "10": "じゅう", "100": "ひゃく", "1000": "せん", "10000": "まん", "100000000": "おく",
                 "300": "さんびゃく", "600": "ろっぴゃく", "800": "はっぴゃく", "3000": "さんぜん", "8000":"はっせん", "01000": "いっせん" }

key_dict = {"kanji" : kanji_dict, "hiragana" : hiragana_dict, "romaji": romaji_dict}

def len_one(convert_num,requested_dict):
    # Returns single digit conversion, 0-9
    return requested_dict[convert_num]

def len_two(convert_num,requested_dict):
    # Returns the conversion, when number is of length two (10-99)
    if convert_num[0] == "0": #if 0 is first, return len_one
        return len_one(convert_num[1],requested_dict)
    if convert_num == "10":
        return requested_dict["10"] # Exception, if number is 10, simple return 10
    if convert_num[0] == "1": # When first number is 1, use ten plus second number
        return requested_dict["10"] + " " + len_one(convert_num[1],requested_dict)
    elif convert_num[1] == "0": # If ending number is zero, give first number plus 10
        return len_one(convert_num[0],requested_dict) + " " + requested_dict["10"]
    else:
        num_list = []
        for x in convert_num:
            num_list.append(requested_dict[x])
        num_list.insert(1, requested_dict["10"])
        # Convert to a string (from a list)
        output = ""
        for y in num_list:
            output += y + " "
        output = output[:len(output) - 1]  # take off the space
        return output

def len_three(convert_num,requested_dict):
    # Returns the conversion, when number is of length three (100-999)
    num_list = []
    if convert_num[0] == "1":
        num_list.append(requested_dict["100"])
    elif convert_num[0] == "3":
        num_list.append(requested_dict["300"])
    elif convert_num[0] == "6":
        num_list.append(requested_dict["600"])
    elif convert_num[0] == "8":
        num_list.append(requested_dict["800"])
    else:
        num_list.append(requested_dict[convert_num[0]])
        num_list.append(requested_dict["100"])
    if convert_num[1:] == "00" and len(convert_num) == 3:
        pass
    else:
        if convert_num[1] == "0":
            num_list.append(requested_dict[convert_num[2]])
        else:
            num_list.append(len_two(convert_num[1:], requested_dict))
    output = ""  
    for y in num_list:
         output += y + " "
    output = output[:len(output) - 1]
    return output

def len_four(convert_num,requested_dict, stand_alone):
    # Returns the conversion, when number is of length four (1000-9999)
    num_list = []
    # First, check for zeros (and get deal with them)
    if convert_num == "0000":
        return ""
    while convert_num[0] == "0":
        convert_num = convert_num[1:]
    if len(convert_num) == 1:
        return len_one(convert_num,requested_dict)
    elif len(convert_num) == 2:
        return len_two(convert_num,requested_dict)
    elif len(convert_num) == 3:
        return len_three(convert_num,requested_dict)
    # If no zeros, do the calculation
    else:
        # Have to handle 1000, depending on if its a standalone 1000-9999 or included in a larger number
        if convert_num[0] == "1" and stand_alone:
            num_list.append(requested_dict["1000"])
        elif convert_num[0] == "1":
            num_list.append(requested_dict["01000"])
        elif convert_num[0] == "3":
            num_list.append(requested_dict["3000"])
        elif convert_num[0] == "8":
            num_list.append(requested_dict["8000"])
        else:
            num_list.append(requested_dict[convert_num[0]])
            num_list.append(requested_dict["1000"])
        if convert_num[1:] == "000" and len(convert_num) == 4:
            pass
        else:
            if convert_num[1] == "0":
                num_list.append(len_two(convert_num[2:],requested_dict))
            else:
                num_list.append(len_three(convert_num[1:],requested_dict))
        output = ""
        for y in num_list:
             output += y + " "
        output = output[:len(output) - 1]
        return output


def len_x(convert_num,requested_dict):
    #Returns everything else.. (up to 9 digits)
    num_list = []
    if len(convert_num[0:-4]) == 1:
        num_list.append(requested_dict[convert_num[0:-4]])
        num_list.append(requested_dict["10000"])
    elif len(convert_num[0:-4]) == 2:
        num_list.append(len_two(convert_num[0:2],requested_dict))
        num_list.append(requested_dict["10000"])
    elif len(convert_num[0:-4]) == 3:
        num_list.append(len_three(convert_num[0:3],requested_dict))
        num_list.append(requested_dict["10000"])
    elif len(convert_num[0:-4]) == 4:
        num_list.append(len_four(convert_num[0:4],requested_dict, False))
        num_list.append(requested_dict["10000"])
    elif len(convert_num[0:-4]) == 5:
        num_list.append(requested_dict[convert_num[0]])
        num_list.append(requested_dict["100000000"])
        num_list.append(len_four(convert_num[1:5],requested_dict, False))
        if convert_num[1:5] == "0000":
            pass
        else:
            num_list.append(requested_dict["10000"])
    else:
        assert False, "Not yet implemented, please choose a lower number."
    num_list.append(len_four(convert_num[-4:],requested_dict, False))
    output = ""
    for y in num_list:
         output += y + " "
    output = output[:len(output) - 1]       
    return output

def remove_spaces(convert_result):
    # Remove spaces in Hirigana and Kanji results
    correction = ""
    for x in convert_result:
        if x == " ":
            pass
        else:
         correction += x
    return correction

def do_convert(convert_num,requested_dict):
    #Check lengths and convert accordingly
    if len(convert_num) == 1:
        return(len_one(convert_num,requested_dict))
    elif len(convert_num) == 2:
        return(len_two(convert_num,requested_dict))
    elif len(convert_num) == 3:
        return(len_three(convert_num,requested_dict))
    elif len(convert_num) == 4:
        return(len_four(convert_num,requested_dict, True))
    else:
        return(len_x(convert_num,requested_dict))

def split_Point(split_num,dict_choice):
    # Used if a decmial point is in the string.
    split_num = split_num.split(".")
    split_num_a = split_num[0]
    split_num_b = split_num[1]
    split_num_b_end = " "
    for x in split_num_b:
        split_num_b_end += len_one(x,key_dict[dict_choice]) + " "
    # To account for small exception of small tsu when ending in jyuu in hiragana/romaji
    if split_num_a[-1] == "0" and split_num_a[-2] != "0" and dict_choice == "hiragana":
        small_Tsu = Convert(split_num_a,dict_choice)
        small_Tsu = small_Tsu[0:-1] + "っ"
        return small_Tsu + key_dict[dict_choice]["."] + split_num_b_end
    if split_num_a[-1] == "0" and split_num_a[-2] != "0" and dict_choice == "romaji":
        small_Tsu = Convert(split_num_a,dict_choice)
        small_Tsu = small_Tsu[0:-1] + "t"
        return small_Tsu + key_dict[dict_choice]["."] + split_num_b_end

    return Convert(split_num_a,dict_choice) + " " + key_dict[dict_choice]["."] + split_num_b_end


def do_kanji_convert(convert_num):
    # Converts kanji to arabic number

    if convert_num == "零":
        return 0

    # First, needs to check for MAN 万 and OKU 億 kanji, as need to handle differently, splitting up the numbers at these intervals.
    # key tells us whether we need to add or multiply the numbers, then we create a list of numbers in an order we need to add/multiply
    key = []
    numberList = []
    y = ""
    for x in convert_num:
        if x == "万" or x == "億":
            numberList.append(y)
            key.append("times")
            numberList.append(x)
            key.append("plus")
            y = ""
        else:
            y += x
    if y != "":
        numberList.append(y)

    numberListConverted = []
    baseNumber = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
    linkNumber = ["十", "百", "千", "万", "億"]

    # Converts the kanji number list to arabic numbers, using the 'base number' and 'link number' list above. For a link number, we would need to
    # link with a base number
    for noX in numberList:
        count = len(noX)
        result = 0
        skip = 1
        for x in reversed(noX):
            addTo = 0
            skip -= 1
            count = count - 1
            if skip == 1:
                continue
            if x in baseNumber:
                for y, z in kanji_dict.items():
                    if z == x:
                        result += int(y)
            elif x in linkNumber:
                if noX[count - 1] in baseNumber and count > 0:
                    for y, z in kanji_dict.items():
                        if z == noX[count - 1]:
                            tempNo = int(y)
                            for y, z in kanji_dict.items():
                                if z == x:
                                    addTo += tempNo * int(y)
                                    result += addTo
                                    skip = 2
                else:
                    for y, z in kanji_dict.items():
                        if z == x:
                            result += int(y)
        numberListConverted.append(int(result))

    result = numberListConverted[0]
    y = 0

    # Iterate over the converted list, and either multiply/add as instructed in key list
    for x in range(1,len(numberListConverted)):
        if key[y] == "plus":
            try:
                if key[y+1] == "times":
                    result = result + numberListConverted[x] * numberListConverted[x+1]
                    y += 1
                else:
                    result += numberListConverted[x]
            except IndexError:
                result += numberListConverted[-1]
                break
        else:
            result = result * numberListConverted[x]
        y += 1

    return result

def Convert(convert_num, dict_choice='hiragana'):
    # Input formatting
    convert_num = str(convert_num)
    convert_num = convert_num.replace(',','')
    dict_choice = dict_choice.lower()

    # If all is selected as dict_choice, return as a list
    if dict_choice == "all":
        result_list = []
        for x in "kanji", "hiragana", "romaji":
            result_list.append(Convert(convert_num,x))
        return result_list

    dictionary = key_dict[dict_choice]
    
    # Exit if length is greater than current limit
    if len(convert_num) > 9:
        return("Number length too long, choose less than 10 digits")

    # Remove any leading zeroes
    while convert_num[0] == "0" and len(convert_num) > 1:
        convert_num = convert_num[1:]

    # Check for decimal places
    if "." in convert_num:
        result = split_Point(convert_num,dict_choice)
    else:
        result = do_convert(convert_num, dictionary)

    # Remove spaces and return result
    if key_dict[dict_choice] == romaji_dict:
        pass
    else:
        result = remove_spaces(result)
    return result

def ConvertKanji(convert_num):
    if convert_num[0] in kanji_dict.values():
        # Check to see if 点 (point) is in the input, and handle by splitting at 点, before and after is handled separately
        if "点" in convert_num:
            point = convert_num.find("点")
            endNumber = ""
            for x in convert_num[point+1:]:
                endNumber += list(kanji_dict.keys())[list(kanji_dict.values()).index(x)]
            return(str(do_kanji_convert(convert_num[0:point])) + "." + endNumber)
        else:
            return(str(do_kanji_convert(convert_num)))
