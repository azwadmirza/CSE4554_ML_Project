    def save_help(event, module_name, help_text):
        """Save the help text for a module"""
        save_dlg = wx.FileDialog(event.GetEventObject(),
                                 message="Save help for %s to file" % module_name,
                                 defaultFile="%s.html" % module_name,
                                 wildcard="*.html",
                                 style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = save_dlg.ShowModal()
        if result == wx.ID_OK:
            pathname = save_dlg.GetPath()
            fd = open(pathname, "wt")
            fd.write(help_text)
            fd.close()