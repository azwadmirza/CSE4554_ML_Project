    def create(self, fn):
        """Create the given file with empty contents."""
        theDir = g.os_path_dirname(fn)
        # Make the directories as needed.
        ok = g.makeAllNonExistentDirectories(
            theDir, c=self.c, force=True, verbose=True)
        # #1453: Don't assume the directory exists.
        if not ok:
            g.error(f"did not create: {theDir}")
            return
        try:
            f = open(fn, mode='wb')
            f.close()
            g.note(f"created: {fn}")
        except IOError:
            g.error(f"can not create: {fn}")
        except Exception:
            g.error(f"unexpected error creating: {fn}")
            g.es_exception()