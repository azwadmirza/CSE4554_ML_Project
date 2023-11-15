    def _onText(self, chr):
        """Called by the window when characters are received"""
        if chr == '\t':
            self.win.nextEditable()
            return
        if chr == '\r':  # make it newline not Carriage Return
            chr = '\n'
        txt = self.text
        self.text = txt[:self.caret.index] + chr + txt[self.caret.index:]
        self.caret.index += 1
        if self.onTextCallback:
            self.onTextCallback()