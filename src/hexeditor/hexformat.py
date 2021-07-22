import re
import binascii


_p0 = re.compile(r"""^[^0-9A-Fa-f]*\x00[^0-9A-Fa-f]*|
                     [^0-9A-Fa-f]*\x00""", re.VERBOSE)
_p1 = re.compile(r"""[0-9A-Fa-f]\x00(?=[0-9A-Fa-f][0-9A-Fa-f])|
                     [0-9A-Fa-f][0-9A-Fa-f](?=\x00[0-9A-Fa-f])|
                     [0-9A-Fa-f]\x00[0-9A-Fa-f]|
                     [0-9A-Fa-f][0-9A-Fa-f]\x00|
                     \x00[0-9A-Fa-f][0-9A-Fa-f]|
                     [0-9A-Fa-f]\x00|
                     [0-9A-Fa-f][0-9A-Fa-f]|
                     \x00[0-9A-Fa-f]|
                     [0-9A-Fa-f]|
                     \x00""", re.VERBOSE)
_p3 = re.compile(r"[0-9A-Fa-f]{1,2}")
_p4 = re.compile(r"[^\x20-\x7e]")


def _hexformat(hex):
    return ' '.join('0' + m if m != "\x00" and len(m) == 1 else m for m in _p1.findall(_p0.sub("\x00", hex))).upper()


def hexformat(hex, pos):
    hex2 = _hexformat(hex[:pos] + "\x00" + hex[pos:])
    pos2 = hex2.find("\x00")
    if pos2 >= 0:
        return (hex2[:pos2] + hex2[pos2+1:], pos2)
    raise ValueError("unexpected value")


def hex2bin(hex):
    return ''.join(chr(int(s, 16) & 0xFF) for s in _p3.findall(hex))


def bin2hex(bin):
    return _hexformat(binascii.b2a_hex(bin))


def bin2asc(bin):
    return _p4.sub('.', bin)


def fix_bin(asc, pos, bin):
    n = len(asc) - len(bin)
    if n > 0:  # append
        return bin[:pos-n] + asc[pos-n:pos] + bin[pos-n:]
    elif n < 0:  # delete
        return bin[:pos] + bin[pos-n:]
    else:  # modify
        return ''.join(asc if asc != '.' else r for asc, r in zip(asc, bin))
