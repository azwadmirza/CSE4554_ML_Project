    def openFileHelper(self, fileName):
        """Open a file, reporting all exceptions."""
        at = self
        s = ''
        try:
            with open(fileName, 'rb') as f:
                s = f.read()
        except IOError:
            at.error(f"can not open {fileName}")
        except Exception:
            at.error(f"Exception reading {fileName}")
            g.es_exception()
        return s