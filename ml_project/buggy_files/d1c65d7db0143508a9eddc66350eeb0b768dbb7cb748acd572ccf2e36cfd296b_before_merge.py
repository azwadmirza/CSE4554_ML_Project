    def readOpenedLeoFile(self, c, fn, readAtFileNodesFlag, theFile):
        # New in Leo 4.10: The open1 event does not allow an override of the init logic.
        assert theFile
        # lm = self
        ok = c.fileCommands.openLeoFile(theFile, fn,
            readAtFileNodesFlag=readAtFileNodesFlag)
                # closes file.
        if ok:
            if not c.openDirectory:
                theDir = c.os_path_finalize(g.os_path_dirname(fn))
                c.openDirectory = c.frame.openDirectory = theDir
        else:
            g.app.closeLeoWindow(c.frame, finish_quit=self.more_cmdline_files is False)
        return ok