import binascii
import re

p_acceptable = re.compile(r'[0-9A-Fa-f ]+$')
p_hex3chars = re.compile(r'\b[0-9A-Fa-f]{3,}\b')
p_hex1chars = re.compile(r'\b([0-9A-Za-z])\b')


def decode(value):
    return binascii.a2b_hex(fmtasc(value))


def fmtasc(value):
    if not p_acceptable.match(value):
        raise ValueError("unacceptable characters", value)
    elif p_hex3chars.search(value):
        ret = value.replace(' ', '')
        if len(ret) % 2 == 0:
            return ret
        else:
            return '0' + ret
    else:
        return p_hex1chars.sub("0\\1", value).replace(' ', '')


def test():
    print decode('01 02 03 04') == "\x01\x02\x03\x04"
    print decode('1 2 3 4') == "\x01\x02\x03\x04"
    print decode('AB c DE F') == "\xAB\x0C\xDE\x0F"
    print decode('ABC D E F') == "\xAB\xCD\xEF"
    try:
        print decode('ABCDEFG')
    except ValueError as e:
        print e


test()