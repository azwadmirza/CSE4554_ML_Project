    def updateTab(self, p, w, smartTab=True):
        """
        A helper for selfInsertCommand.

        Add spaces equivalent to a tab.
        """
        c = self.c
        i, j = w.getSelectionRange()
            # Returns insert point if no selection, with i <= j.
        if i != j:
            c.indentBody()
            return
        tab_width = c.getTabWidth(p)
        # Get the preceeding characters.
        s = w.getAllText()
        start, end = g.getLine(s, i)
        after = s[i:end]
        if after.endswith('\n'):
            after = after[:-1]
        # Only do smart tab at the start of a blank line.
        doSmartTab = (smartTab and c.smart_tab and i == start)
            # Truly at the start of the line.
            # and not after # Nothing *at all* after the cursor.
        if doSmartTab:
            self.updateAutoIndent(p, w)
            # Add a tab if otherwise nothing would happen.
            if s == w.getAllText():
                self.doPlainTab(s, i, tab_width, w)
        else:
            self.doPlainTab(s, i, tab_width, w)