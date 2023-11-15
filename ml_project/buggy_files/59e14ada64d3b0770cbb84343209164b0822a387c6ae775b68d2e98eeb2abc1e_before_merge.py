def _executables_in_posix(path):
    if PYTHON_VERSION_INFO < (3, 5, 0):
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            if (os.path.exists(fpath) and
                    os.access(fpath, os.X_OK) and
                    (not os.path.isdir(fpath))):
                yield fname
    else:
        yield from _yield_accessible_unix_file_names(path)