    def copyObject(self, event):
        if wx.TheClipboard.Open():
            # Get color rounded
            col = getattr(self.color, self.ctrls.GetCurrentPage().space)
            if isinstance(col, tuple):
                col = tuple(round(c, 2) for c in col)
            # Copy to clipboard
            wx.TheClipboard.SetData(wx.TextDataObject(
                "Color("+str(col)+", \'"+self.ctrls.GetCurrentPage().space+"\')"
            ))
            wx.TheClipboard.Close()