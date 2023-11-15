    def __init__(self, path, cause=None):
        path = os.path.relpath(path)
        super(StageFileCorruptedError, self).__init__(
            "unable to read stage file: {} "
            "YAML file structure is corrupted".format(path),
            cause=cause,
        )