    def __init__(self, opts):
        self.opts = opts
        self.process_manager = salt.utils.process.ProcessManager(name='NetAPIProcessManager')
        self.netapi = salt.loader.netapi(self.opts)