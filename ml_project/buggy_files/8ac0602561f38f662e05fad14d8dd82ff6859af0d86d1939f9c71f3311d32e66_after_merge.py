    def __init__(self, args, as_module=False):
        self.args = args
        self.as_module = as_module

        self.arg0 = args[0]
        self.package = self.modulename = self.pathname = self.loader = self.spec = None