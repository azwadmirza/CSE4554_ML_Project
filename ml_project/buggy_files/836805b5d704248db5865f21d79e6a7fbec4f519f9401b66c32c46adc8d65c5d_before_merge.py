    def checkForOpenFile(self, c, fn):
        """Warn if fn is already open and add fn to already_open_files list."""
        d, tag = g.app.db, 'open-leo-files'
        if g.app.reverting:
            # Fix #302: revert to saved doesn't reset external file change monitoring
            g.app.already_open_files = []
        if (d is None or
            g.app.unitTesting or
            g.app.batchMode or
            g.app.reverting or
            g.app.inBridge
        ):
            return
        aList = g.app.db.get(tag) or []
        if [x for x in aList if os.path.samefile(x, fn)]:
            # The file may be open in another copy of Leo, or not:
            # another Leo may have been killed prematurely.
            # Put the file on the global list.
            # A dialog will warn the user such files later.
            if fn not in g.app.already_open_files:
                g.es('may be open in another Leo:', color='red')
                g.es(fn)
                g.app.already_open_files.append(fn)
        else:
            g.app.rememberOpenFile(fn)