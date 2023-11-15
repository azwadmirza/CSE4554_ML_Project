    def insertNewLineAndTab(self, event):
        """Insert a newline and tab at the cursor."""
        trace = 'keys' in g.app.debug
        c, k = self.c, self.c.k
        p = c.p
        w = self.editWidget(event)
        if not w:
            return
        if not g.isTextWrapper(w):
            return
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        if trace: g.trace('(newline-and-indent)')
        self.beginCommand(w, undoType='insert-newline-and-indent')
        oldSel = w.getSelectionRange()
        self.insertNewlineHelper(w=w, oldSel=oldSel, undoType=None)
        self.updateTab(p, w, smartTab=False)
        k.setInputState('insert')
        k.showStateAndMode()
        self.endCommand(changed=True, setLabel=False)