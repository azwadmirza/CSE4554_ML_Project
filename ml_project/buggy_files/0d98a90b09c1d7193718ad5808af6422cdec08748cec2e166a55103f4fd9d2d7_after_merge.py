    def _valid_dirname(self, path):
        path = os.path.abspath(path)
        if path == self.tree_root:
            return True
        dirname, basename = os.path.split(path)
        dirs, _ = self.dvcignore(dirname, [basename], [])
        if dirs:
            return True
        return False