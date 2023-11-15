    def set_options(self, options):

        super(CallbackModule, self).set_options(options)

        # get options
        try:
            self.api_url = self._plugin_options['api']
            self.api_port = self._plugin_options['port']
            self.api_tls_port = self._plugin_options['tls_port']
            self.use_tls = self._plugin_options['use_tls']
            self.flatten = self._plugin_options['flatten']
        except KeyError as e:
            self._display.warning("Missing option for Logentries callback plugin: %s" % to_native(e))
            self.disabled = True

        try:
            self.token = self._plugin_options['token']
        except KeyError as e:
            self._display.warning('Logentries token was not provided, this is required for this callback to operate, disabling')
            self.disabled = True

        if self.flatten and not HAS_FLATDICT:
            self.disabled = True
            self._display.warning('You have chosen to flatten and the `flatdict` python module is not installed.\nDisabling the Logentries callback plugin.')

        self._initialize_connections()