    def _valid_dirname(self, path):
        dirname, basename = os.path.split(os.path.normpath(path))
        dirs, _ = self.dvcignore(os.path.abspath(dirname), [basename], [])
        if dirs:
            return True
        return False