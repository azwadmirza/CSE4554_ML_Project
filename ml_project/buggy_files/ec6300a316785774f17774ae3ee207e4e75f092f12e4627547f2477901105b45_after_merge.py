    def _iter_non_pyc_files(cls, directory):
        # type: (str) -> Iterator[str]
        normpath = os.path.realpath(os.path.normpath(directory))
        for root, dirs, files in os.walk(normpath):
            dirs[:] = list(filter_pyc_dirs(dirs))
            for f in filter_pyc_files(files):
                yield os.path.relpath(os.path.join(root, f), normpath)