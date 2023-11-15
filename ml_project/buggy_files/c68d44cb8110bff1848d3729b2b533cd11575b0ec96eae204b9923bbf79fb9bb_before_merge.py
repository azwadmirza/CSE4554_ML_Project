    def _stash(self, path):
        return os.path.join(
            self.save_dir.path, os.path.splitdrive(path)[1].lstrip(os.path.sep)
        )