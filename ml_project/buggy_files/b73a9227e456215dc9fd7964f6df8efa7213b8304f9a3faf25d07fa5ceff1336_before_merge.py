    def __init__(self, opts):
        self.opts = opts
        self.process_manager = salt.utils.process.ProcessManager()
        self.netapi = salt.loader.netapi(self.opts)