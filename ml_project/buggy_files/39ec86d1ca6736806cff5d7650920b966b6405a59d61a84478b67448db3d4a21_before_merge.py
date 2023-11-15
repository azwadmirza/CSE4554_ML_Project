    def initialize(self, argv=None):
        """Initialize application, notebooks, writer, and postprocessor"""
        self.init_syspath()
        super().initialize(argv)
        self.init_notebooks()
        self.init_writer()
        self.init_postprocessor()