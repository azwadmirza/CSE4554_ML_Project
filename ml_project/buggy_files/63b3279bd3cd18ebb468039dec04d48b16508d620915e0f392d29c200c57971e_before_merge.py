    def add(self, paths: Iterable[str]):
        from dvc.utils.fs import walk_files

        if isinstance(paths, str):
            paths = [paths]

        files = []
        for path in paths:
            if not os.path.isabs(path):
                path = os.path.join(self.root_dir, path)
            if os.path.isdir(path):
                files.extend(walk_files(path))
            else:
                files.append(path)

        for fpath in files:
            # NOTE: this doesn't check gitignore, same as GitPythonBackend.add
            self.repo.stage(relpath(fpath, self.root_dir))