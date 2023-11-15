    def __init__(self, ctx: DistributedContext, op,
                 log_path: str, custom_log_meta):
        self.ctx = ctx
        self.op = op
        self.log_path = log_path
        self.custom_log_meta = custom_log_meta

        self.file = open(log_path, 'w')
        self.stdout = sys.stdout
        # flag about registering log path
        self.is_log_path_registered = False