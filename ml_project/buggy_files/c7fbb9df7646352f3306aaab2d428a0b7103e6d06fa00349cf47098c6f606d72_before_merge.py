    def writePathChanged(self, p):
        '''
        raise IOError if p's path has changed *and* user forbids the write.
        '''
        at, c = self, self.c
        #
        # Suppress this message during save-as and save-to commands.
        if c.ignoreChangedPaths:
            return
        oldPath = g.os_path_normcase(at.getPathUa(p))
        newPath = g.os_path_normcase(g.fullPath(c, p))
        try:  # #1367: samefile can throw IOError!
            changed = oldPath and not os.path.samefile(oldPath, newPath)
        except IOError:
            changed = True
        if not changed:
            return
        ok = at.promptForDangerousWrite(
            fileName=None,
            message=(
                f"{g.tr('path changed for %s' % (p.h))}\n"
                f"{g.tr('write this file anyway?')}"
            ),
        )
        if not ok:
            raise IOError
        at.setPathUa(p, newPath)  # Remember that we have changed paths.