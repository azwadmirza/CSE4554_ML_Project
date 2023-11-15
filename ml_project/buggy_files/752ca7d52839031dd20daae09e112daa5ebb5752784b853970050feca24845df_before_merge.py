    def updateAfterTyping(self, p, w):
        """
        Perform all update tasks after changing body text.
        
        This is ugly, ad-hoc code, but should be done uniformly.
        """
        c = self.c
        if g.isTextWrapper(w):
            # An important, ever-present unit test.
            all = w.getAllText()
            if g.unitTesting:
                assert p.b == all, g.callers()
            elif p.b != all:
                g.trace(f"\nError:p.b != w.getAllText() p:{p.h} {g.callers()}\n")
                # g.printObj(g.splitLines(p.b), tag='p.b')
                # g.printObj(g.splitLines(all), tag='getAllText')
            p.v.insertSpot = ins = w.getInsertPoint()
            # From u.doTyping.
            newSel = w.getSelectionRange()
            if newSel is None:
                p.v.selectionStart, p.v.selectionLength = (ins, 0)
            else:
                i, j = newSel
                p.v.selectionStart, p.v.selectionLength = (i, j - i)
        else:
            if g.unitTesting:
                assert False, f"Not a text wrapper: {g.callers()}"
            g.trace('Not a text wrapper')
            p.v.insertSpot = 0
            p.v.selectionStart, p.v.selectionLength = (0, 0)
        #
        # #1749.
        if p.isDirty():
            redraw_flag = False
        else:
            p.setDirty() # Do not call p.v.setDirty!
            redraw_flag = True
        if not c.isChanged():
            c.setChanged()
        # Update editors.
        c.frame.body.updateEditors()
        # Update icons.
        val = p.computeIcon()
        if not hasattr(p.v, "iconVal") or val != p.v.iconVal:
            p.v.iconVal = val
            redraw_flag = True
        #
        # Recolor the body.
        c.frame.scanForTabWidth(p)  # Calls frame.setTabWidth()
        c.recolor()
        if g.app.unitTesting:
            g.app.unitTestDict['colorized'] = True
        if redraw_flag:
            c.redraw_after_icons_changed()
        w.setFocus()