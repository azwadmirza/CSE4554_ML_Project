    def __init__(self, options):

        self.options = options
        roles_paths = getattr(self.options, 'roles_path', [])
        if isinstance(roles_paths, string_types):
            self.roles_paths = [os.path.expanduser(roles_path) for roles_path in roles_paths.split(os.pathsep)]

        self.roles =  {}

        # load data path for resource usage
        this_dir, this_filename = os.path.split(__file__)
        self.DATA_PATH = os.path.join(this_dir, "data")

        self._default_readme = None
        self._default_meta = None
        self._default_test = None
        self._default_travis = None