    def replaceClipboardWith(self, s):
        '''Replace the clipboard with the string s.'''
        root = Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(s)
        root.destroy()