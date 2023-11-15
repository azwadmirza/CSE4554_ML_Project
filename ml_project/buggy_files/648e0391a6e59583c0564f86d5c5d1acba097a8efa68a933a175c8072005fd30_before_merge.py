    def open_by_relpath(self, path, remote=None, mode="r", encoding=None):
        """Opens a specified resource as a file descriptor"""

        tree = RepoTree(self, stream=True, subrepos=True)
        path = os.path.join(self.root_dir, path)
        try:
            with self.state:
                with tree.open(
                    path, mode=mode, encoding=encoding, remote=remote,
                ) as fobj:
                    yield fobj
        except FileNotFoundError as exc:
            raise FileMissingError(path) from exc
        except IsADirectoryError as exc:
            raise DvcIsADirectoryError(f"'{path}' is a directory") from exc