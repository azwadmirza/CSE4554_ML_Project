    def __init__(self, config):
        path = config.core.db_filename
        config_dir, config_file = os.path.split(config.filename)
        config_name, _ = os.path.splitext(config_file)
        if path is None:
            path = os.path.join(config_dir, config_name + '.db')
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.normpath(os.path.join(config_dir, path))
        self.filename = path
        self._create()