import wx
import json
from hexeditor import hexeditor


class ExportFileDropTarget(wx.FileDropTarget):

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDragOver(self, x, y, defResult):
        return wx.DragCopy

    def OnDropFiles(self, x, y, filenames):
        for filepath in filenames:
            self.window.SetValue(filepath)
            return True
        return False


class ExportDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Save As")
        self._binPath = wx.TextCtrl(self, size=(200, -1))
        button1 = wx.Button(self, label="...", size=(20, -1))
        self._pemPath = wx.TextCtrl(self, size=(200, -1))
        button2 = wx.Button(self, label="...", size=(20, -1))
        self._pemPass = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self._pemPath.SetDropTarget(ExportFileDropTarget(self._pemPath))
        gbs = wx.GridBagSizer(vgap=5, hgap=5)
        gbs.Add(wx.StaticText(self, label="Package File (*.bin):"), (0, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self._binPath, (0, 1), flag=wx.EXPAND)
        gbs.Add(button1, (0, 2), flag=wx.EXPAND)
        gbs.Add(wx.StaticLine(self), (1, 0), (1, 3), flag=wx.EXPAND)
        gbs.Add(wx.StaticText(self, label="Key File (*.pem):"), (2, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self._pemPath, (2, 1), flag=wx.EXPAND)
        gbs.Add(button2, (2, 2), flag=wx.EXPAND)
        gbs.Add(wx.StaticText(self, label="Password:"), (3, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self._pemPass, (3, 1), flag=wx.EXPAND)
        gbs.AddGrowableCol(1)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(gbs, 0, wx.EXPAND | wx.ALL, 10)
        box.AddStretchSpacer()
        box.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.BOTTOM, 10)
        self.SetSizer(box)
        self.Fit()
        self.CenterOnParent()
        button1.Bind(wx.EVT_BUTTON, self.OnBinPathSelect)
        button2.Bind(wx.EVT_BUTTON, self.OnPemPathSelect)

    def GetBinPath(self):
        return self._binPath.GetValue()

    def GetPemPath(self):
        return self._pemPath.GetValue()

    def GetPemPass(self):
        return self._pemPass.GetValue()

    def OnBinPathSelect(self, evt):
        dlg = wx.FileDialog(parent=self,
                            message="Save As",
                            wildcard="Package File (*.bin)|*.bin",
                            defaultFile="package.bin",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() != wx.ID_OK:
            return
        self._binPath.SetValue(dlg.GetPath())

    def OnPemPathSelect(self, evt):
        dlg = wx.FileDialog(parent=self,
                            message="PEM File",
                            wildcard="PEM File (*.pem)|*.pem",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() != wx.ID_OK:
            return
        self._pemPath.SetValue(dlg.GetPath())


class EditDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Edit Value")
        self._name = wx.ComboBox(self)
        self._edit = hexeditor.HexEditor(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._name, 0, wx.EXPAND | wx.ALL, 8)
        sizer.Add(self._edit, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 8)
        sizer.AddStretchSpacer()
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 8)
        self.SetSizer(sizer)
        self.CenterOnParent()

    def SetName(self, name):
        self._name.SetValue(name)

    def SetHexValue(self, value):
        self._edit.SetHexValue(value)

    def GetName(self):
        return self._name.GetValue()

    def GetAscValue(self):
        return self._edit.GetAscValue()

    def GetHexValue(self):
        return self._edit.GetHexValue()


class ListPanel(wx.Panel):

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
        self._list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.NO_BORDER)
        self._list.SetColumnWidth(self._list.AppendColumn("Name"), 100)
        self._list.SetColumnWidth(self._list.AppendColumn("ASC"), 100)
        self._list.SetColumnWidth(self._list.AppendColumn("HEX"), 100)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._list, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEditItem)
        self._list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self._list.Bind(wx.EVT_MENU, self.OnExport, id=self.MENU_EXPORT)
        self._list.Bind(wx.EVT_MENU, self.OnEditItem, id=self.MENU_EDIT_ITEM)
        self._list.Bind(wx.EVT_MENU, self.OnCopyName, id=self.MENU_COPY_NAME)
        self._list.Bind(wx.EVT_MENU, self.OnCopyAsc, id=self.MENU_COPY_ASC)
        self._list.Bind(wx.EVT_MENU, self.OnCopyHex, id=self.MENU_COPY_HEX)

    def OnEditItem(self, evt):
        item = self._list.GetFirstSelected()
        if item < -1:
            return
        dlg = EditDialog(self)
        dlg.SetName(self._list.GetItemText(item, self.COL_NAME))
        dlg.SetHexValue(self._list.GetItemText(item, self.COL_HEX))
        if dlg.ShowModal() != wx.ID_OK:
            return
        self._list.SetItem(item, self.COL_NAME, dlg.GetName())
        self._list.SetItem(item, self.COL_ASC, dlg.GetAscValue())
        self._list.SetItem(item, self.COL_HEX, dlg.GetHexValue())

    def Populate(self, items):
        for item in items:
            self._list.Append(item)

    def AppendItem(self):
        dlg = EditDialog(self)
        ret = dlg.ShowModal()
        if ret != wx.ID_OK:
            return
        self._list.Append((dlg.GetName(), dlg.GetAscValue(), dlg.GetHexValue()))

    def DeleteItem(self):
        item = -1
        while True:
            item = self._list.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1:
                break
            self._list.DeleteItem(item)
            item = -1

    def OnRightClick(self, evt):
        menu = wx.Menu()
        menu.Append(self.MENU_EXPORT, "Export")
        item = self._list.GetFirstSelected()
        if item >= 0:
            name = self._list.GetItemText(item, self.COL_NAME)
            asc = self._list.GetItemText(item, self.COL_ASC)
            hex = self._list.GetItemText(item, self.COL_HEX)
            menu.AppendSeparator()
            menu.Append(self.MENU_EDIT_ITEM, "Edit Item")
            menu.AppendSeparator()
            menu.Append(self.MENU_COPY_NAME, "Copy Name \"{}\"".format(name))
            menu.Append(self.MENU_COPY_ASC, "Copy Asc \"{}\"".format(asc))
            menu.Append(self.MENU_COPY_HEX, "Copy Hex \"{}\"".format(hex))
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
        self._list.PopupMenu(menu)
        menu.Destroy()

    def OnCopyName(self, evt):
        self.CopySelectedItem(self.COL_NAME)

    def OnCopyAsc(self, evt):
        self.CopySelectedItem(self.COL_ASC)

    def OnCopyHex(self, evt):
        self.CopySelectedItem(self.COL_HEX)

    def CopySelectedItem(self, col):
        item = self._list.GetFirstSelected()
        if item < 0:
            return
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self._list.GetItemText(item, col)))
            wx.TheClipboard.Close()

    def OnExport(self, evt):
        dlg = ExportDialog(self)
        if dlg.ShowModal() != wx.ID_OK:
            return
        items = []
        item = 0
        while item < self._list.GetItemCount():
            items.append((self._list.GetItemText(item, self.COL_NAME),
                          self._list.GetItemText(item, self.COL_ASC),
                          self._list.GetItemText(item, self.COL_HEX)))
            item += 1
        with open(dlg.GetBinPath(), "w") as fp:
            json.dump(items, fp)


class AppFrame(wx.Frame):

    ICON_SIZE = (16, 16)
    ID_APPEND = 10
    ID_DELETE = 20

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        bmAppend = wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR, self.ICON_SIZE)
        bmDelete = wx.ArtProvider.GetBitmap(wx.ART_MINUS, wx.ART_TOOLBAR, self.ICON_SIZE)
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        toolbar.SetToolBitmapSize(self.ICON_SIZE)
        toolbar.AddTool(self.ID_APPEND, "Append", bmAppend)
        toolbar.AddTool(self.ID_DELETE, "Delete", bmDelete)
        toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.ID_APPEND)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=self.ID_DELETE)
        self.list = ListPanel(self)

    def OnToolClick(self, evt):
        eventId = evt.GetId()
        if eventId == self.ID_APPEND:
            self.list.AppendItem()
        elif eventId == self.ID_DELETE:
            self.list.DeleteItem()


def main():
    app = wx.App()
    frame = AppFrame(None, title="Test Frame")
    frame.SetSize((800, 600))
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
