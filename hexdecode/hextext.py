from binascii import b2a_hex, a2b_hex
import re
import wx
import string


def filterhexdigits(value):
    return filter(lambda c: c in string.hexdigits, value)


def formathexdigits(value):
    return re.sub(r"([0-9A-Fa-f]{2})", "\\1 ", filterhexdigits(value))


def renderHex(pos, value):
    pref = formathexdigits(value[:pos]).rstrip()
    suff = value[pos:].lstrip()
    if len(pref) % 3 == 1 and len(suff) > 0:
        ret = pref + suff[0] + " " + formathexdigits(suff[1:])
    else:
        ret = pref + " " + formathexdigits(suff)
    return (len(pref), ret.strip().upper())


def formatprintable(value):
    return re.sub(r"[^\x20-\x7e]", ".", value)


def renderAsc(pos, value, rawvalue):
    d = len(value) - len(rawvalue)
    if d < 0:  # deleted
        rawvalue = rawvalue[:pos] + rawvalue[pos - d:]
    elif d > 0:  # added
        rawvalue = rawvalue[:pos - d] + value[pos - d:pos] + rawvalue[pos - d:]
    elif formatprintable(rawvalue) != value:  # changed?
        rawvalue = value
    return rawvalue


class HexText(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._text1 = wx.TextCtrl(self)
        self._text1.Bind(wx.EVT_TEXT, self.OnHexFormat)
        self._text2 = wx.TextCtrl(self)
        self._text2.Bind(wx.EVT_TEXT, self.OnAscFormat)
        sizer = wx.FlexGridSizer(cols=2, vgap=2, hgap=2)
        sizer.Add(wx.StaticText(self, label="HEX:"), 0,
                  wx.SHRINK | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._text1, 1, wx.EXPAND)
        sizer.Add(wx.StaticText(self, label="Asc:"), 0,
                  wx.SHRINK | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._text2, 1, wx.EXPAND)
        sizer.AddGrowableCol(1)
        self.SetSizer(sizer)
        self._rawvalue = ""

    def OnHexFormat(self, evt):
        textctrl = evt.GetEventObject()
        pos = textctrl.GetInsertionPoint()
        value = textctrl.GetValue()
        # set the value to text2 as binary
        hexvalue = filterhexdigits(value)
        if len(hexvalue) % 2 == 0:
            self._rawvalue = a2b_hex(hexvalue)
        else:
            self._rawvalue = a2b_hex(hexvalue + "0")
        self._text2.ChangeValue(formatprintable(self._rawvalue))
        # format the value for text1 as text
        newpos, ascvalue = renderHex(pos, value)
        textctrl.ChangeValue(ascvalue)
        textctrl.SetInsertionPoint(newpos)

    def OnAscFormat(self, evt):
        textctrl = evt.GetEventObject()
        pos = textctrl.GetInsertionPoint()
        value = textctrl.GetValue()
        self._rawvalue = renderAsc(pos, str(value), self._rawvalue)
        self._text1.ChangeValue(formathexdigits(b2a_hex(self._rawvalue)))


class MyPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(HexText(self), 1, wx.EXPAND)
        self.SetSizer(sizer)


def main():
    app = wx.App()
    frame = wx.Frame(None)
    MyPanel(frame)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
