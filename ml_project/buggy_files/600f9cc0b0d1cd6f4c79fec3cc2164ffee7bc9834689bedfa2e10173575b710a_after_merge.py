    def __on_browse(self, event, edit_box, text):
        dir_dialog = wx.DirDialog(
            self.__panel, str.capitalize(text), edit_box.GetValue()
        )
        if dir_dialog.ShowModal() == wx.ID_OK:
            edit_box.SetValue(dir_dialog.GetPath())
            fake_event = wx.CommandEvent(wx.wxEVT_COMMAND_TEXT_UPDATED)
            fake_event.SetEventObject(edit_box)
            fake_event.SetId(edit_box.Id)
            edit_box.GetEventHandler().ProcessEvent(fake_event)