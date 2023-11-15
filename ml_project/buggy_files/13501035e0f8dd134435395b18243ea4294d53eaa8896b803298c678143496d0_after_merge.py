    def __init__(self, spec, path, installed, ref_count=0):
        self.spec = spec
        self.path = str(path)
        self.installed = bool(installed)
        self.ref_count = ref_count