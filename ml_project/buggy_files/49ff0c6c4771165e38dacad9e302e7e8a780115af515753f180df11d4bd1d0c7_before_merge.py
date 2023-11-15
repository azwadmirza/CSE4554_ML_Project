    def __init__(self, spec: importlib.machinery.ModuleSpec, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec: importlib.machinery.ModuleSpec = spec