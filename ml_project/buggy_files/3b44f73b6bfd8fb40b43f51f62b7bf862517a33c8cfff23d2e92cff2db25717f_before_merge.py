    def __init__(self, path, **kwargs):
        self._path = path
        if isinstance(path, (Path, WindowsPath, PosixPath, LocalPath)):
            path = str(path.absolute())
        elif path is not None:
            path = str(path)

        self.cwd = Path.cwd()
        _lt_folder = Path(_localtrack_folder) if _localtrack_folder else self.cwd
        _path = Path(path) if path else self.cwd

        if _lt_folder.parts[-1].lower() == "localtracks" and not kwargs.get("forced"):
            self.localtrack_folder = _lt_folder
        elif kwargs.get("forced"):
            if _path.parts[-1].lower() == "localtracks":
                self.localtrack_folder = _path
            else:
                self.localtrack_folder = _path / "localtracks"
        else:
            self.localtrack_folder = _lt_folder / "localtracks"

        try:
            _path = Path(path)
            _path.relative_to(self.localtrack_folder)
            self.path = _path
        except (ValueError, TypeError):
            if path and path.startswith("localtracks//"):
                path = path.replace("localtracks//", "", 1)
            elif path and path.startswith("localtracks/"):
                path = path.replace("localtracks/", "", 1)
            self.path = self.localtrack_folder.joinpath(path) if path else self.localtrack_folder

        try:
            if self.path.is_file():
                parent = self.path.parent
            else:
                parent = self.path
            super().__init__(str(parent.absolute()))

            self.parent = Path(parent)
        except OSError:
            self.parent = None

        self.cwd = Path.cwd()