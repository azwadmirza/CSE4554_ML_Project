    def create(self, fn):
        """Create the given file with empty contents."""
        theDir = g.os_path_dirname(fn)
        g.makeAllNonExistentDirectories(theDir, c=self.c, force=True, verbose=True)
            # Make the directories as needed.
        try:
            f = open(fn, mode='wb')
            f.close()
            g.note(f"created: {fn}")
        except IOError:
            g.error(f"can not create: {fn}")
        except Exception:
            g.error(f"unexpected error creating: {fn}")
            g.es_exception()