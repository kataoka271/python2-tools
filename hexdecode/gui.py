import wx
import binascii
import re
import json
from hexdecode import hexdecode
from diff import diffget


class ExportFileDropTarget(wx.FileDropTarget):

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDragOver(self, x, y, defResult):
        return wx.DragCopy

    def OnDropFiles(self, x, y, filenames):
        for filepath in filenames:
            if filepath.endswith(self.suffix):
                self.window.SetValue(filepath)  
                return True
        return False


class ExportDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Export", size=(-1, 400))
        self._txt_bin_path = wx.TextCtrl(self, size=(200, -1))
        self._btn_bin_path = wx.Button(self, label="...", size=(20, -1))
        self._txt_key_path = wx.TextCtrl(self, size=(200, -1))
        self._btn_key_path = wx.Button(self, label="...", size=(20, -1))
        self._txt_password = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self._txt_key_path.SetDropTarget(ExportFileDropTarget(self._txt_key_path))
        gbs = wx.GridBagSizer(vgap=5, hgap=5)
        gbs.Add(wx.StaticText(self, label="Bin File (*.bin):"), (0, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self._txt_bin_path, (0, 1), flag=wx.EXPAND)
        gbs.Add(self._btn_bin_path, (0, 2), flag=wx.EXPAND)
        gbs.Add(wx.StaticLine(self), (1, 0), (1, 3), flag=wx.EXPAND)
        gbs.Add(wx.StaticText(self, label="Key File (*.pem):"), (2, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self._txt_key_path, (2, 1), flag=wx.EXPAND)
        gbs.Add(self._btn_key_path, (2, 2), flag=wx.EXPAND)
        gbs.Add(wx.StaticText(self, label="Password:"), (3, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self._txt_password, (3, 1), flag=wx.EXPAND)
        gbs.AddGrowableCol(1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gbs, 0, wx.EXPAND | wx.ALL, 10)
        sizer.AddStretchSpacer()
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.BOTTOM, 10)
        self.SetSizer(sizer)
        self.Fit()
        self.CenterOnParent()
        self._btn_bin_path.Bind(wx.EVT_BUTTON, self.OnBinFileFind)
        self._btn_key_path.Bind(wx.EVT_BUTTON, self.OnKeyFileFind)

    def OnBinFileFind(self, evt):
        dlg = wx.FileDialog(self, "Save As", wildcard="Bin file (*.bin)|*.bin", defaultFile="package.bin", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self._txt_bin_path.SetValue(dlg.GetPath())

    def OnKeyFileFind(self, evt):
        dlg = wx.FileDialog(self, "Key file", wildcard="Key file (*.pem)|*.pem", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self._txt_keyfile.SetValue(dlg.GetPath())

    def GetBinPath(self):
        return self._txt_bin_path.GetValue()

    def GetKeyPath(self):
        return self._txt_key_path.GetValue()

    def GetPassword(self):
        return self._txt_password.GetValue()

    def SetBinPath(self, value):
        return self._txt_bin_path.SetValue(value)

    def SetKeyPath(self, value):
        return self._txt_key_path.SetValue(value)

    def SetPassword(self, value):
        return self._txt_password.SetValue(value)


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
    MENU_EXPORT = wx.NewId()
    MENU_EDIT_ITEM = wx.NewId()
    MENU_COPY_NAME = wx.NewId()
    MENU_COPY_ASC = wx.NewId()
    MENU_COPY_HEX = wx.NewId()

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._lc = wx.ListCtrl(self, style=wx.LC_REPORT | wx.NO_BORDER)
        self._lc.SetColumnWidth(self._lc.AppendColumn("Name"), 100)
        self._lc.SetColumnWidth(self._lc.AppendColumn("ASC"), 100)
        self._lc.SetColumnWidth(self._lc.AppendColumn("HEX"), 100)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._lc, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self._Populate()
        self._lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEditItem)
        self._lc.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self._lc.Bind(wx.EVT_MENU, self.OnExport, id=self.MENU_EXPORT)
        self._lc.Bind(wx.EVT_MENU, self.OnEditItem, id=self.MENU_EDIT_ITEM)
        self._lc.Bind(wx.EVT_MENU, self.OnCopyName, id=self.MENU_COPY_NAME)
        self._lc.Bind(wx.EVT_MENU, self.OnCopyAsc, id=self.MENU_COPY_ASC)
        self._lc.Bind(wx.EVT_MENU, self.OnCopyHex, id=self.MENU_COPY_HEX)

    def OnEditItem(self, evt):
        item = self._lc.GetFirstSelected()
        if item < -1:
            return
        dialog = MyDialog(self)
        dialog.SetName(self._lc.GetItemText(item, self.COL_NAME))
        dialog.SetHexValue(self._lc.GetItemText(item, self.COL_HEX))
        if dialog.ShowModal() == wx.ID_OK:
            self._lc.SetItem(item, self.COL_NAME, dialog.GetName())
            self._lc.SetItem(item, self.COL_ASC, dialog.GetAscValue())
            self._lc.SetItem(item, self.COL_HEX, dialog.GetHexValue())

    def _Populate(self):
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

    def OnRightClick(self, evt):
        menu = wx.Menu()
        menu.Append(self.MENU_EXPORT, "Export")
        item = self._lc.GetFirstSelected()
        if item >= 0:
            name = self._lc.GetItemText(item, self.COL_NAME)
            asc = self._lc.GetItemText(item, self.COL_ASC)
            hex_ = self._lc.GetItemText(item, self.COL_HEX)
            menu.AppendSeparator()
            menu.Append(self.MENU_EDIT_ITEM, "Edit Item")
            menu.AppendSeparator()
            menu.Append(self.MENU_COPY_NAME, "Copy Name \"{}\"".format(name))
            menu.Append(self.MENU_COPY_ASC, "Copy Asc \"{}\"".format(asc))
            menu.Append(self.MENU_COPY_HEX, "Copy Hex \"{}\"".format(hex_))
        else:
            menu.AppendSeparator()
            menu.Append(self.MENU_EDIT_ITEM, "Edit Item")
            menu.AppendSeparator()
            menu.Append(self.MENU_COPY_NAME, "Copy Name")
            menu.Append(self.MENU_COPY_ASC, "Copy Asc")
            menu.Append(self.MENU_COPY_HEX, "Copy Hex")
            menu.Enable(self.MENU_EDIT_ITEM, False)
            menu.Enable(self.MENU_COPY_NAME, False)
            menu.Enable(self.MENU_COPY_ASC, False)
            menu.Enable(self.MENU_COPY_HEX, False)
        self._lc.PopupMenu(menu)
        menu.Destroy()

    def OnCopyName(self, evt):
        self._OnCopyItem(self.COL_NAME)

    def OnCopyAsc(self, evt):
        self._OnCopyItem(self.COL_ASC)

    def OnCopyHex(self, evt):
        self._OnCopyItem(self.COL_HEX)

    def _OnCopyItem(self, col):
        item = self._lc.GetFirstSelected()
        if item < 0:
            return
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self._lc.GetItemText(item, col)))
            wx.TheClipboard.Close()            

    def OnExport(self, evt):
        dialog = ExportDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            print (dialog.GetBinPath(), dialog.GetKeyPath(), dialog.GetPassword())
            ls = []
            item = 0
            while item < self._lc.GetItemCount():
                ls.append((self._lc.GetItemText(item, self.COL_NAME),
                           self._lc.GetItemText(item, self.COL_ASC),
                           self._lc.GetItemText(item, self.COL_HEX)))
                item += 1
            with open(dialog.GetBinPath(), "w") as fp:
                json.dump(ls, fp)


class MyFrame(wx.Frame):

    TSIZE = (16, 16)
    ID_APPEND = 10
    ID_DELETE = 20

    def __init__(self, parent, title, size=(-1, -1)):
        wx.Frame.__init__(self, parent, title=title, size=size)
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