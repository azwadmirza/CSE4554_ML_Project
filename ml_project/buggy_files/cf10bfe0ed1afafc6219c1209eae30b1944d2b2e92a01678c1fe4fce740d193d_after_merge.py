    def __init__(self, path, localtrack_folder, **kwargs):
        self._localtrack_folder = localtrack_folder
        self._path = path
        if isinstance(path, (Path, WindowsPath, PosixPath, LocalPath)):
            path = str(path.absolute())
        elif path is not None:
            path = str(path)

        self.cwd = Path.cwd()
        _lt_folder = Path(self._localtrack_folder) if self._localtrack_folder else self.cwd
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
            for sep in _PATH_SEPS:
                if path and path.startswith(f"localtracks{sep}{sep}"):
                    path = path.replace(f"localtracks{sep}{sep}", "", 1)
                elif path and path.startswith(f"localtracks{sep}"):
                    path = path.replace(f"localtracks{sep}", "", 1)
            self.path = self.localtrack_folder.joinpath(path) if path else self.localtrack_folder

        try:
            if self.path.is_file():
                parent = self.path.parent
            else:
                parent = self.path
            self.parent = Path(parent)
        except OSError:
            self.parent = None