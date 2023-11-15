    def is_ignored(self, path):
        # NOTE: can't use self.check_ignore(path).match for now, see
        # https://github.com/iterative/dvc/issues/4555
        if os.path.isfile(path):
            return self.is_ignored_file(path)
        if os.path.isdir(path):
            return self.is_ignored_dir(path)
        return self.is_ignored_file(path) or self.is_ignored_dir(path)