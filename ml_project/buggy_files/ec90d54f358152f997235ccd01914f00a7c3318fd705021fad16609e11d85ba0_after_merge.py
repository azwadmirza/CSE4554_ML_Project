    def shouldPromptForDangerousWrite(self, fn, p):
        '''
        Return True if Leo should warn the user that p is an @<file> node that
        was not read during startup. Writing that file might cause data loss.
        
        See #50: https://github.com/leo-editor/leo-editor/issues/50
        '''
        trace = 'save' in g.app.debug
        sfn = g.shortFileName(fn)
        c = self.c
        efc = g.app.externalFilesController
        if p.isAtNoSentFileNode():
            # #1450.
            # No danger of overwriting a file.
            # It was never read.
            return False
        if not g.os_path_exists(fn):
            # No danger of overwriting fn.
            if trace: g.trace('Return False: does not exist:', sfn)
            return False
        # #1347: Prompt if the external file is newer.
        if efc:
            # Like c.checkFileTimeStamp.
            if c.sqlite_connection and c.mFileName == fn:
                # sqlite database file is never actually overwriten by Leo,
                # so do *not* check its timestamp.
                pass
            elif efc.has_changed(c, fn):
                if trace: g.trace('Return True: changed:', sfn)
                return True
        if hasattr(p.v, 'at_read'):
            # Fix bug #50: body text lost switching @file to @auto-rst
            d = p.v.at_read
            for k in d:
                # Fix bug # #1469: make sure k still exists.
                if (
                    os.path.exists(k) and os.path.samefile(k, fn)
                    and p.h in d.get(k, set())
                ):
                    d[fn] = d[k]
                    if trace: g.trace('Return False: in p.v.at_read:', sfn)
                    return False
            aSet = d.get(fn, set())
            if trace:
                g.trace(f"Return {p.h not in aSet()}: p.h not in aSet(): {sfn}")
            return p.h not in aSet
        if trace:
            g.trace('Return True: never read:', sfn)
        return True  # The file was never read.