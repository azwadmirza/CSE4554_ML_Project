    def getTextFromClipboard(self):
        '''Get a unicode string from the clipboard.'''
        # Fix #971.
        if not Tk:
            return g.u('')
        root = Tk()
        root.withdraw()
        try:
            s = root.clipboard_get()
        except Exception: # _tkinter.TclError:
            s = ''
        root.destroy()
        return g.toUnicode(s)