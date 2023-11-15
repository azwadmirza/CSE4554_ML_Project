    def save_help(event, module_name, help_text):
        """Save the help text for a module"""
        save_dlg = wx.FileDialog(event.GetEventObject().GetWindow(),
                                 message="Save help for %s to file" % module_name,
                                 defaultFile="%s.html" % module_name,
                                 wildcard="*.html",
                                 style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        result = save_dlg.ShowModal()

        if result == wx.ID_OK:
            with codecs.open(save_dlg.GetPath(), "w", encoding="utf-8") as fd:
                fd.write("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />")
                fd.write(help_text)