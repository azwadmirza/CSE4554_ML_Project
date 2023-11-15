    def __init__(self, ctx: DistributedContext, op,
                 log_path: str):
        self.ctx = ctx
        self.op = op
        self.log_path = log_path

        self.file = open(log_path, 'w')
        self.stdout = sys.stdout

        self.raw_stdout = self.stdout
        while isinstance(self.raw_stdout, _LogWrapper):
            self.raw_stdout = self.raw_stdout.stdout

        # flag about registering log path
        self.is_log_path_registered = False