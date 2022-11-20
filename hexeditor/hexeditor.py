import wx
import hexformat


class HexEditor(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._bin = ""
        self._hex = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self._hex.Bind(wx.EVT_TEXT, self.OnHexText)
        self._asc = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self._asc.Bind(wx.EVT_TEXT, self.OnAscText)
        sizer = wx.FlexGridSizer(cols=2, vgap=2, hgap=2)
        sizer.Add(wx.StaticText(self, label="Hex:"), 0, wx.SHRINK | wx.ALIGN_TOP | wx.TOP, border=2)
        sizer.Add(self._hex, 1, wx.EXPAND)
        sizer.Add(wx.StaticText(self, label="Asc:"), 0, wx.SHRINK | wx.ALIGN_TOP | wx.TOP, border=2)
        sizer.Add(self._asc, 1, wx.EXPAND)
        sizer.AddGrowableCol(1)
        self.SetSizer(sizer)

    def OnHexText(self, evt):
        pos = self._hex.GetInsertionPoint()
        hex = self._hex.GetValue()
        newhex, newpos = hexformat.hexformat(hex.encode('utf-8'), pos)
        self._bin = hexformat.hex2bin(newhex)
        self._asc.ChangeValue(hexformat.bin2asc(self._bin))
        self._hex.ChangeValue(newhex)
        self._hex.SetInsertionPoint(newpos)

    def OnAscText(self, evt):
        pos = self._asc.GetInsertionPoint()
        asc = self._asc.GetValue()
        self._bin = hexformat.fix_bin(asc.encode('utf-8'), pos, self._bin)
        self._hex.ChangeValue(hexformat.bin2hex(self._bin))

    def SetBinValue(self, value):
        self._bin = value
        self._hex.ChangeValue(hexformat.bin2hex(value))
        self._asc.ChangeValue(hexformat.bin2asc(value))

    def SetHexValue(self, value):
        self.SetBinValue(hexformat.hex2bin(value))

    def GetBinValue(self):
        return self._bin

    def GetHexValue(self):
        return hexformat.bin2hex(self._bin)

    def GetAscValue(self):
        return hexformat.bin2asc(self._bin)


def main():
    app = wx.App()
    frame = wx.Frame(None)
    edit = HexEditor(frame)
    edit.SetBinValue("aa\x0020")
    frame.Show()
    app.MainLoop()
    print(repr(edit.GetBinValue()))


if __name__ == '__main__':
    main()
