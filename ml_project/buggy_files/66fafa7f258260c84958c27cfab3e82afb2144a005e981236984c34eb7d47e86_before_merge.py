    def openFileByName(self, fn, gui, old_c, previousSettings):
        '''Read the local file whose full path is fn using the given gui.
        fn may be a Leo file (including .leo or zipped file) or an external file.

        This is not a pre-read: the previousSettings always exist and
        the commander created here persists until the user closes the outline.

        Reads the entire outline if fn exists and is a .leo file or zipped file.
        Creates an empty outline if fn is a non-existent Leo file.
        Creates an wrapper outline if fn is an external file, existing or not.
        '''
        lm = self
        # Disable the log.
        g.app.setLog(None)
        g.app.lockLog()
        # Create the a commander for the .leo file.
        # Important.  The settings don't matter for pre-reads!
        # For second read, the settings for the file are *exactly* previousSettings.
        c = g.app.newCommander(fileName=fn, gui=gui,
            previousSettings=previousSettings)
        assert c
        # Open the file, if possible.
        g.doHook('open0')
        theFile = lm.openLeoOrZipFile(fn)
        if isinstance(theFile, sqlite3.Connection):
            # this commander is associated with sqlite db
            c.sqlite_connection = theFile
            
        # Enable the log.
        g.app.unlockLog()
        c.frame.log.enable(True)
        # Phase 2: Create the outline.
        g.doHook("open1", old_c=None, c=c, new_c=c, fileName=fn)
        if theFile:
            readAtFileNodesFlag = bool(previousSettings)
            # The log is not set properly here.
            ok = lm.readOpenedLeoFile(c, fn, readAtFileNodesFlag, theFile)
                # Call c.fileCommands.openLeoFile to read the .leo file.
            if not ok: return None
        else:
            # Create a wrapper .leo file if:
            # a) fn is a .leo file that does not exist or
            # b) fn is an external file, existing or not.
            lm.initWrapperLeoFile(c, fn)
        g.doHook("open2", old_c=None, c=c, new_c=c, fileName=fn)
        # Phase 3: Complete the initialization.
        g.app.writeWaitingLog(c)
        c.setLog()
        lm.createMenu(c, fn)
        lm.finishOpen(c)
        return c