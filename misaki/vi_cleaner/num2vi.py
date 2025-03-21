# Vietnamese Number Converter
# Sauce: https://github.com/ngthuong45/vietnam-number
# No license
# Fix grammar error of using "lẽ" instead of "lẻ" (https://github.com/ngthuong45/vietnam-number/issues/5)
# Works up to 12 figures (999.999.999.999)

units = {
    '0': 'không',
    '1': 'một',
    '2': 'hai',
    '3': 'ba',
    '4': 'bốn',
    '5': 'năm',
    '6': 'sáu',
    '7': 'bảy',
    '8': 'tám',
    '9': 'chín',
}

def chunks(lst, n):
    """Hàm chia nhỏ danh sách đầu vào.

    Hàm dùng chia nhỏ danh sách đầu vào thành các nhóm danh sách con với số lượng các phần tử trong
    nhóm con là n

    Args:
        lst: Danh sách đầu vào.
        n: Số lượng phần tử trong một nhóm con.

    Returns:
        Danh sách các nhóm con có n phần tử.
    """
    chunks_lst = []
    for i in range(0, len(lst), n):
        chunks_lst.append(lst[i : i + n])

    return chunks_lst

def n2w_units(numbers: str):
    """Hàm chuyển đổi số sang chữ số cho hàng đơn vị.

    Args:
        numbers (str): Chuỗi số đầu vào.

    Returns:
        Chuỗi chữ số đầu ra.

    Raises:
        ValueError: Số đầu vào là rỗng.
        ValueError: Số đầu vào có giá trị lớn hơn 9.

    """

    if not numbers:
        raise ValueError('Số rỗng!! vui lòng nhập số đúng định dạng!')

    if len(numbers) > 1:
        raise ValueError('Số vượt quá giá trị của hàng đơn vị!')

    return units[numbers]

def pre_process_n2w(number: str):
    """Hàm tiền xữ lý dữ liệu đầu vào.

    Args:
        number (str): Chuỗi số đầu vào.

    Returns:
        Chuỗi số sau khi được tiền xữ lý.
    """
    clean_number = ''

    char_to_replace = {
        ' ': '',
        '-': '',
        '.': '',
        ',': '',
    }

    # xóa các ký tự đặt biệt
    for key, value in char_to_replace.items():
        number = number.replace(key, value)

    # Kiểm tra tính hợp lệ của đầu vào
    if not number.isdigit():
        raise ValueError('Đầu vào không phải là kiểu chuỗi chỉ chứa các ký tự số (isdigit)!')

    # xóa các ký tự số không có trong unit
    for element in number:
        if element in units:
            clean_number += element

    # Thông báo lỗi nếu người dùng nhập đầu vào không hợp lệ!
    if not clean_number:
        raise ValueError("Số không hợp lệ, vui lòng nhập số đúng định dạng!")

    return clean_number

def process_n2w_single(numbers: str):
    """Hàm chuyển đổi số sang chữ số theo từng số một.

    Args:
        numbers (str): Chuỗi số đầu vào.

    Returns:
        Chuỗi chữ số đầu ra.
    """
    total_number = ''
    for element in numbers:
        total_number += units[element] + ' '

    return total_number.strip()

def n2w_hundreds(numbers: str):
    """Hàm chuyển đổi số sang chữ số lớp trăm.

    Hàm chuyển đổi số sang chữ số áp dụng cho các số từ 0 đến 999

    Args:
        numbers (str): Chuỗi số đầu vào.

    Returns:
        Chuỗi chữ số đầu ra.

    Raises:
        ValueError: Nếu số đầu vào lớn hơn 999.
        ValueError: Nếu số đầu vào là chuỗi rỗng.

    """
    if len(numbers) > 3:
        raise ValueError('Số vượt quá giá trị của hàng trăm!')

    if len(numbers) == 0:
        raise ValueError('Số vượt quá giá trị của hàng trăm!')

    if len(numbers) <= 1:
        return n2w_units(numbers)

    # Chúng ta cần duyệt danh sách từ phải qua trái nhằm phân biệt các giá trị từ nhỏ đến lớn.
    # Lý giải: giả sử chúng ta có 2 đầu vào: '10' và '123'
    # tại vị trí index đầu tiên của 2 chuỗi điều có giá trị là 1
    # tuy nhiên, chuỗi đầu 1 là giá trị của hàng chục.
    # chuỗi cuối 1 là giá trị của hàng trăm.
    reversed_hundreds = numbers[::-1]

    total_number = []
    for e in range(0, len(reversed_hundreds)):

        if e == 0:
            total_number.append(units[reversed_hundreds[e]])
        elif e == 1:
            total_number.append(units[reversed_hundreds[e]] + ' mươi ')
        elif e == 2:
            total_number.append(units[reversed_hundreds[e]] + ' trăm ')

    # vd: ta có total_number = ['không', 'hai mươi ', 'một trăm ']
    # có nghĩa là ta muốn kết quả cuối cùng là: ['một trăm ', 'hai mươi ', 'không']
    # Các trường hợp đặc biệt:
    #       1. 'hai mươi không' trở thành 'hai mươi'
    #       2. 'ba trăm không mươi hai' trở thành 'ba trăm lẻ hai'
    #       3. 'một mươi một' trở thành 'mười một'
    #       4. 'hai mươi một' trở thành 'hai mươi mốt'
    #       5. 'một mươi năm' trở thành 'mười lăm'
    #       6. 'hai trăm ba mươi năm' trở thành 'hai trăm ba mươi lăm'
    #       7. 'hai trăm không mươi ba' trở thành 'hai trăm lẻ ba'
    for idx, value in enumerate(total_number):
        if idx == 0 and value == 'không':

            if total_number[1] == 'không mươi ':
                total_number[1] = ''

            total_number[idx] = ''

        if idx == 0 and value == 'một':
            if total_number[1] != 'một mươi ' and total_number[1] != 'không mươi ':
                total_number[idx] = 'mốt'

        if idx == 0 and value == 'năm':
            if total_number[1] != 'không mươi ':
                total_number[idx] = 'lăm'

        if value == 'không mươi ':
            total_number[idx] = 'lẻ '

        if value == 'một mươi ':
            total_number[idx] = 'mười '

    return ''.join(total_number[::-1]).strip()

def n2w_large_number(numbers: str):
    """Hàm chuyển đổi các số có giá trị lớn.

    Hàm chuyển đổi các số có giá trị lớn từ 999 đến 999.999.999.999

    Args:
        numbers (str): Chuỗi số đầu vào.

    Returns:
        Chuỗi chữ số đầu ra.

    """
    # Chúng ta cần duyệt chuổi số đầu vào từ phải sang trái nhằm phân biệt các giá trị từ nhỏ đến lớn.
    # tương tự như khi chúng ta xữ lý cho hàm n2w_hundreds
    reversed_large_number = numbers[::-1]

    # Chia chuỗi số đầu vào thành các nhóm con có 3 phần tử.
    # vì cứ 3 phần tử số lại tạo thành một lớp giá trị, như lớp trăm, lớp nghìn, lớp triệu...
    reversed_large_number = chunks(reversed_large_number, 3)

    total_number = []
    for e in range(0, len(reversed_large_number)):

        if e == 0:
            value_of_hundred = reversed_large_number[0][::-1]
            total_number.append(n2w_hundreds(value_of_hundred))
        if e == 1:
            value_of_thousand = reversed_large_number[1][::-1]
            total_number.append(n2w_hundreds(value_of_thousand) + ' nghìn ')
        if e == 2:
            value_of_million = reversed_large_number[2][::-1]
            total_number.append(n2w_hundreds(value_of_million) + ' triệu ')
        if e == 3:
            value_of_billion = reversed_large_number[3][::-1]
            total_number.append(n2w_hundreds(value_of_billion) + ' tỷ ')

    return ''.join(total_number[::-1]).strip()

def n2w(number: str):
    # Tiền xữ lý dữ liệu chuỗi số đầu vào
    clean_number = pre_process_n2w(number)

    return n2w_large_number(clean_number)

def n2w_single(number: str):
    # Xữ lý đặc thù dành cho số điện thoại
    if number[0:3] == '+84':
        number = number.replace('+84', '0')

    # Tiền xữ lý dữ liệu chuỗi số đầu vào
    clean_number = pre_process_n2w(number)

    return process_n2w_single(clean_number)

__all__ = ["n2w", "n2w_single"]