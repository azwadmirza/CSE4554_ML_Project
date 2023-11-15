    def openEmptyWorkBook(self):
        """Open an empty frame and paste the contents of CheatSheet.leo into it."""
        lm = self
        # Create an empty frame.
        fn = lm.computeWorkbookFileName()
        if not fn:
            return None # #1415
        c = lm.loadLocalFile(fn, gui=g.app.gui, old_c=None)
        if not c:
            return None # #1201: AttributeError below.
        # Open the cheatsheet, but not in batch mode.
        if not g.app.batchMode and not g.os_path_exists(fn):
            # #933: Save clipboard.
            old_clipboard = g.app.gui.getTextFromClipboard()
            # Paste the contents of CheetSheet.leo into c.
            c2 = c.openCheatSheet(redraw=False)
            if c2:
                for p2 in c2.rootPosition().self_and_siblings():
                    c2.setCurrentPosition(p2) # 1380
                    c2.copyOutline()
                    p = c.pasteOutline()
                    # #1380 & #1381: Add guard & use vnode methods to prevent redraw.
                    if p:
                        c.setCurrentPosition(p) # 1380
                        p.v.contract()
                        p.v.clearDirty()
                c2.close(new_c=c)
                # Delete the dummy first node.
                root = c.rootPosition()
                root.doDelete(newNode=root.next())
                c.target_language = 'rest'
                    # Settings not parsed the first time.
                c.setChanged(False)
                c.redraw(c.rootPosition()) # # 1380: Select the root.
            # #933: Restore clipboard
            g.app.gui.replaceClipboardWith(old_clipboard)
        return c