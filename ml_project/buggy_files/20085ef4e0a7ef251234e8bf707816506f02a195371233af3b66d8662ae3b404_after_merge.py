    def initialize(self, options):
        """
        """
        _default_region(options)
        _default_account_id(options)
        if options.tracer and options.tracer.startswith('xray') and HAVE_XRAY:
            XrayTracer.initialize()

        return options