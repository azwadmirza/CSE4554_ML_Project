    def __init__(self, command, cwd=None, shell=False, environment=None,
                 combine_output=True, input_data=None, build_env=None,
                 bin_path=None):
        self.command = command
        self.shell = shell
        if cwd is None:
            cwd = os.getcwd()
        self.cwd = cwd
        self.environment = os.environ.copy()
        if environment is not None:
            self.environment.update(environment)
        self.combine_output = combine_output
        self.build_env = build_env
        self.bin_path = bin_path
        self.status = None
        self.input_data = input_data
        self.output = None
        self.error = None