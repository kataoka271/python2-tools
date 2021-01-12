import wx
import binascii
import re
from hexdecode import hexdecode
from diff import diffget


class MyDialog(wx.Dialog):

    _p_notascii = re.compile(r"[^\x20-\x7E]") 
    _p_hexchars = re.compile(r"([0-9A-Fa-f]{2}) *")
    _p_nothexchars = re.compile(r"[^0-9A-Fa-f ]+")

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Edit Value", size=(-1, 180))
        self._cb_name = wx.ComboBox(self)
        self._txt_asc = wx.TextCtrl(self)
        self._txt_hex = wx.TextCtrl(self)
        flex = wx.FlexGridSizer(2, vgap=5, hgap=5)
        flex.AddGrowableCol(1)
        flex.Add(wx.StaticText(self, label="Name:"), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        flex.Add(self._cb_name, 0, wx.EXPAND)
        flex.Add(wx.StaticText(self, label="ASC:"), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        flex.Add(self._txt_asc, 0, wx.EXPAND)
        flex.Add(wx.StaticText(self, label="HEX:"), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        flex.Add(self._txt_hex, 0, wx.EXPAND)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(flex, 0, wx.EXPAND | wx.ALL, 10)
        sizer.AddStretchSpacer()
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.BOTTOM, 10)
        self.SetSizer(sizer)
        self.CenterOnParent()
        self._txt_asc.Bind(wx.EVT_TEXT, self.OnAscText)
        self._txt_hex.Bind(wx.EVT_TEXT, self.OnHexText)
        self._txt_hex.Bind(wx.EVT_CHAR, self.OnHexChar)
        self._value = ""

    def OnAscText(self, evt):
        value = self._txt_asc.GetValue()
        if not value:
            self._value = ""
            self._txt_hex.ChangeValue("")
        else:
            rawvalue = diffget(self._value, value.encode('cp932'))[1]
            self._value = rawvalue
            self._txt_hex.ChangeValue(self._format(binascii.b2a_hex(rawvalue)))

    def OnHexText(self, evt):
        value = self._txt_hex.GetValue()
        if not value:
            self._value = ""
            self._txt_asc.ChangeValue("")
        else:
            newvalue = self._format(self._p_notascii.sub("", value))
            pos = self._txt_hex.GetInsertionPoint()
            self._txt_hex.ChangeValue(newvalue)
            pos = pos + len(newvalue) - len(value)
            self._txt_hex.SetInsertionPoint(pos)
            if not newvalue:
                self._value = ""
                self._txt_asc.ChangeValue("")
            else:
                rawvalue = hexdecode(newvalue)
                self._value = rawvalue
                self._txt_asc.ChangeValue(self._p_notascii.sub(".", rawvalue))

    def OnHexChar(self, evt):
        keycode = evt.GetKeyCode()
        if 0x30 <= keycode <= 0x39 or 0x41 <= keycode <= 0x46 or 0x61 <= keycode <= 0x66:
            evt.Skip()
        elif keycode > 0xFF or keycode < 0x20 or keycode == 0x7F:
            evt.Skip()
        else:
            pass

    def _format(self, value):
        return self._p_hexchars.sub(r"\g<1> ", value).strip().upper()

    def SetAscValue(self, value):
        self._txt_asc.SetValue(value)

    def SetHexValue(self, value):
        self._txt_hex.SetValue(self._p_nothexchars.sub("", value))

    def SetName(self, name):
        self._cb_name.SetValue(name)

    def GetAscValue(self):
        return self._txt_asc.GetValue()

    def GetHexValue(self):
        return self._txt_hex.GetValue()

    def GetName(self):
        return self._cb_name.GetValue()


class MyPanel(wx.Panel):

    COL_NAME = 0
    COL_ASC = 1
    COL_HEX = 2

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._lc = wx.ListCtrl(self, style=wx.LC_REPORT | wx.NO_BORDER)
        self._lc.SetColumnWidth(self._lc.AppendColumn("Name"), 100)
        self._lc.SetColumnWidth(self._lc.AppendColumn("ASC"), 100)
        self._lc.SetColumnWidth(self._lc.AppendColumn("HEX"), 100)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._lc, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self._populate()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivate)

    def OnActivate(self, evt):
        index = evt.GetIndex()
        dialog = MyDialog(self)
        dialog.SetName(self._lc.GetItemText(index, self.COL_NAME))
        dialog.SetHexValue(self._lc.GetItemText(index, self.COL_HEX))
        ret = dialog.ShowModal()
        if ret == wx.ID_OK:
            self._lc.SetItem(index, self.COL_NAME, dialog.GetName())
            self._lc.SetItem(index, self.COL_ASC, dialog.GetAscValue())
            self._lc.SetItem(index, self.COL_HEX, dialog.GetHexValue())

    def _populate(self):
        items = [
            ("key", "value", ""),
            ("read", "read", ""),
            ("one", "1", "")
        ]
        for item in items:
            self._lc.Append(item)

    def AppendItem(self):
        dialog = MyDialog(self)
        ret = dialog.ShowModal()
        if ret == wx.ID_OK:
            self._lc.Append((dialog.GetName(), dialog.GetAscValue(), dialog.GetHexValue()))

    def DeleteItem(self):
        item = -1
        while True:
            item = self._lc.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1:
                break
            self._lc.DeleteItem(item)
            item = -1


class MyFrame(wx.Frame):

    TSIZE = (16, 16)
    ID_APPEND = 10
    ID_DELETE = 20

    def __init__(self, parent, title, size=(-1, -1)):
        wx.Frame.__init__(self, parent, title=title, size=size)
        # setup toolbar
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        bmp_append = wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR, self.TSIZE)
        bmp_delete = wx.ArtProvider.GetBitmap(wx.ART_MINUS, wx.ART_TOOLBAR, self.TSIZE)
        tb.SetToolBitmapSize(self.TSIZE)
        tb.AddTool(self.ID_APPEND, "Append", bmp_append)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.ID_APPEND)
        tb.AddTool(self.ID_DELETE, "Delete", bmp_delete)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.ID_DELETE)
        tb.Realize()
        self._panel = MyPanel(self)

    def OnToolClick(self, evt):
        eId = evt.GetId()
        if eId == self.ID_APPEND:
            self._panel.AppendItem()
        elif eId == self.ID_DELETE:
            self._panel.DeleteItem()


def main():
    app = wx.App()
    frame = MyFrame(None, title="Test Frame", size=(800, 500))
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()