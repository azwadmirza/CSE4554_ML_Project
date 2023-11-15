    def set_options(self, options):

        super(CallbackModule, self).set_options(options)

        self.webhook_url = self._plugin_options['webhook_url']
        self.channel = self._plugin_options['channel']
        self.username = self._plugin_options['username']
        self.show_invocation = (self._display.verbosity > 1)

        if self.webhook_url is None:
            self.disabled = True
            self._display.warning('Slack Webhook URL was not provided. The '
                                  'Slack Webhook URL can be provided using '
                                  'the `SLACK_WEBHOOK_URL` environment '
                                  'variable.')