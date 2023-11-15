def executables_in(path):
    """Returns a generator of files in `path` that the user could execute. """
    if PYTHON_VERSION_INFO < (3, 5, 0):
        for i in os.listdir(path):
            name  = os.path.join(path, i)
            if (os.path.exists(name) and os.access(name, os.X_OK) and \
                                    (not os.path.isdir(name))):
                yield i
    else:
        yield from (x.name for x in scandir(path)
                    if x.is_file() and os.access(x.path, os.X_OK))