    def is_tracked(self, path):
        # it is equivalent to `bool(self.git.git.ls_files(path))` by
        # functionality, but ls_files fails on unicode filenames
        path = os.path.relpath(path, self.root_dir)
        return path in [i[0] for i in self.git.index.entries]