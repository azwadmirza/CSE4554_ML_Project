    def initialize(self, options):
        """
        """
        _default_region(options)
        _default_account_id(options)
        if options.tracer:
            XrayTracer.initialize()

        return options