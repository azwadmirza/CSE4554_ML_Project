    def __init__(self, build):
        self.build = build
        self.environment = build.environment
        self.processed_targets = {}
        self.build_to_src = mesonlib.relpath(self.environment.get_source_dir(),
                                             self.environment.get_build_dir())