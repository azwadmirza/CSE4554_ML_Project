    def is_ignored(self, path):
        # NOTE: can't use self.check_ignore(path).match for now, see
        # https://github.com/iterative/dvc/issues/4555
        return self.is_ignored_dir(path) or self.is_ignored_file(path)