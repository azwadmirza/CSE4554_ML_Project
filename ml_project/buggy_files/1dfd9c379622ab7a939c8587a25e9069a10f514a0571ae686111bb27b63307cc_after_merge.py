    def replaceClipboardWith(self, s):
        '''Replace the clipboard with the string s.'''
        if not Tk:
            return
        root = Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(s)
        root.destroy()