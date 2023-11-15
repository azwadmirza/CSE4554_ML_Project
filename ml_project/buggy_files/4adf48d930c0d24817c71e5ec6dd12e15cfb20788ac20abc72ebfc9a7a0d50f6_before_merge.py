    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        self._ssh_shell = None

        self._matched_prompt = None
        self._matched_cmd_prompt = None
        self._matched_pattern = None
        self._last_response = None
        self._history = list()

        self._terminal = None
        self.cliconf = None
        self.paramiko_conn = None

        if self._play_context.verbosity > 3:
            logging.getLogger('paramiko').setLevel(logging.DEBUG)

        if self._network_os:

            self.cliconf = cliconf_loader.get(self._network_os, self)
            if self.cliconf:
                display.vvvv('loaded cliconf plugin for network_os %s' % self._network_os)
                self._sub_plugins.append({'type': 'cliconf', 'name': self._network_os, 'obj': self.cliconf})
            else:
                display.vvvv('unable to load cliconf for network_os %s' % self._network_os)
        else:
            raise AnsibleConnectionFailure(
                'Unable to automatically determine host network os. Please '
                'manually configure ansible_network_os value for this host'
            )
        display.display('network_os is set to %s' % self._network_os, log_only=True)