    def _iter_non_pyc_files(cls, directory):
        # type: (str) -> Iterator[str]
        normpath = os.path.realpath(os.path.normpath(directory))
        for root, dirs, files in os.walk(normpath):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                # For Python 2.7, `.pyc` files are compiled as siblings to `.py` files (there is no
                # __pycache__ dir. We rely on the fact that the temporary files created by CPython
                # have object id (integer) suffixes to avoid picking up either finished `.pyc` files
                # or files where Python bytecode compilation is in-flight; i.e.:
                # `.pyc.0123456789`-style files.
                if not re.search(r"\.pyc(?:\.[0-9]+)?$", f):
                    yield os.path.relpath(os.path.join(root, f), normpath)