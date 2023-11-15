    def openEmptyWorkBook(self):
        '''Open an empty frame and paste the contents of CheatSheet.leo into it.'''
        lm = self
        # Create an empty frame.
        fn = lm.computeWorkbookFileName()
        c = lm.loadLocalFile(fn, gui=g.app.gui, old_c=None)
        # Open the cheatsheet, but not in batch mode.
        if not g.app.batchMode and not g.os_path_exists(fn):
            # #933: Save clipboard.
            old_clipboard = g.app.gui.getTextFromClipboard()
            # Paste the contents of CheetSheet.leo into c.
            c2 = c.openCheatSheet(redraw=False)
            if c2:
                for p2 in c2.rootPosition().self_and_siblings():
                    c2.selectPosition(p2)
                    c2.copyOutline()
                    p = c.pasteOutline()
                    c.selectPosition(p)
                    p.contract()
                    p.clearDirty()
                c2.close(new_c=c)
                root = c.rootPosition()
                if root.h == g.shortFileName(fn):
                    root.doDelete(newNode=root.next())
                p = g.findNodeAnywhere(c, "Leo's cheat sheet")
                if p:
                    c.selectPosition(p)
                    p.expand()
                c.target_language = 'rest'
                    # Settings not parsed the first time.
                c.setChanged(False)
                c.redraw()
            # #933: Restore clipboard
            g.app.gui.replaceClipboardWith(old_clipboard)
        return c