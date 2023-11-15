    def _stash(self, path):
        best = None
        for save_dir in self._save_dirs:
            if not path.startswith(save_dir.original + os.sep):
                continue
            if not best or len(save_dir.original) > len(best.original):
                best = save_dir
        if best is None:
            best = AdjacentTempDirectory(os.path.dirname(path))
            best.create()
            self._save_dirs.append(best)
        return os.path.join(best.path, os.path.relpath(path, best.original))