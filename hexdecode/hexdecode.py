import binascii
import re


_p_acceptable = re.compile(r'[0-9A-Fa-f ]+$')
_p_hex3chars = re.compile(r'\b[0-9A-Fa-f]{3,}\b')
_p_hex1chars = re.compile(r'\b([0-9A-Za-z])\b')


def hexdecode(value):
    return binascii.a2b_hex(_preformat(value))


def _preformat(value):
    if not _p_acceptable.match(value):
        raise ValueError("unacceptable characters", value)
    elif _p_hex3chars.search(value):
        ret = value.replace(' ', '')
        if len(ret) % 2 == 0:
            return ret
        else:
            return '0' + ret
    else:
        return _p_hex1chars.sub("0\\1", value).replace(' ', '')


def _test_decode(x, y):
    print "hexdecode(" + repr(x) + ") == " + repr(y) + " ==> " + repr(hexdecode(x) == y)


def test():
    _test_decode('01 02 03 04', "\x01\x02\x03\x04")
    _test_decode('1 2 3 4', "\x01\x02\x03\x04")
    _test_decode('AB c DE F', "\xAB\x0C\xDE\x0F")
    _test_decode('ABC D E F', "\xAB\xCD\xEF")
    try:
        print hexdecode('ABCDEFG')
    except ValueError as e:
        print e


if __name__ == "__main__":
    test()