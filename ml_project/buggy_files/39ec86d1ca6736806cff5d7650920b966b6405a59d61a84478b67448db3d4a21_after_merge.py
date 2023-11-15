    def initialize(self, argv=None):
        """Initialize application, notebooks, writer, and postprocessor"""
        # See https://bugs.python.org/issue37373 :(
        if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        self.init_syspath()
        super().initialize(argv)
        self.init_notebooks()
        self.init_writer()
        self.init_postprocessor()