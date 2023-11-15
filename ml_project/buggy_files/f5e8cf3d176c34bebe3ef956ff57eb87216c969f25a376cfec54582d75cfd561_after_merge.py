    def openLeoFile(self, fileName):
        '''Open a .leo file, or create a new Leo frame if no fileName is given.'''
        g = self.g
        g.app.silentMode = self.silentMode
        useLog = False
        if self.isOpen():
            self.reopen_cachers()
            fileName = self.completeFileName(fileName)
            c = self.createFrame(fileName)
            g.app.nodeIndices.compute_last_index(c)
                # New in Leo 5.1. An alternate fix for bug #130.
                # When using a bridge Leo might open a file, modify it,
                # close it, reopen it and change it all within one second.
                # In that case, this code must properly compute the next
                # available gnx by scanning the entire outline.
            if useLog:
                g.app.gui.log = log = c.frame.log
                log.isNull = False
                log.enabled = True
            return c
        return None