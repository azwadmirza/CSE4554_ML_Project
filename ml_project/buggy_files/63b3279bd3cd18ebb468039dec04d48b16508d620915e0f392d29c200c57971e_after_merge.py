    def add(self, paths: Iterable[str]):
        from dvc.utils.fs import walk_files

        if isinstance(paths, str):
            paths = [paths]

        files = []
        for path in paths:
            if not os.path.isabs(path) and self._submodules:
                # NOTE: If path is inside a submodule, Dulwich expects the
                # staged paths to be relative to the submodule root (not the
                # parent git repo root). We append path to root_dir here so
                # that the result of relpath(path, root_dir) is actually the
                # path relative to the submodule root.
                path_info = PathInfo(path).relative_to(self.root_dir)
                for sm_path in self._submodules.values():
                    if path_info.isin(sm_path):
                        path = os.path.join(
                            self.root_dir, path_info.relative_to(sm_path)
                        )
                        break
            if os.path.isdir(path):
                files.extend(walk_files(path))
            else:
                files.append(path)

        for fpath in files:
            # NOTE: this doesn't check gitignore, same as GitPythonBackend.add
            self.repo.stage(relpath(fpath, self.root_dir))