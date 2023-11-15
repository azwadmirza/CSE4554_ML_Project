    def set_options(self, options):

        super(CallbackModule, self).set_options(options)

        global DONT_COLORIZE
        DONT_COLORIZE = self._plugin_options['nocolor']