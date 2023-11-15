    def __init__(self, msg, source, name, options):
        self._msg = msg
        self.source = source
        self.name = name
        self.options = options
        super(CompileException, self).__init__()