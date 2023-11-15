    def __init__(self, options):

        self.options = options
        # self.options.roles_path needs to be a list and will be by default
        roles_path = getattr(self.options, 'roles_path', [])
        # cli option handling is responsible for making roles_path a list
        self.roles_paths = roles_path

        self.roles =  {}

        # load data path for resource usage
        this_dir, this_filename = os.path.split(__file__)
        self.DATA_PATH = os.path.join(this_dir, "data")

        self._default_readme = None
        self._default_meta = None
        self._default_test = None
        self._default_travis = None