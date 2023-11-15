    def matches(self, dirname, basename, is_dir=False):
        path = self._get_normalize_path(dirname, basename)
        if not path:
            return False
        return self.ignore(path, is_dir)