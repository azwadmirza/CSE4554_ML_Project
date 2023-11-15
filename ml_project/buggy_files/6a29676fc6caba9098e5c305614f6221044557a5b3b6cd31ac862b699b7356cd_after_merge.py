    def initialize_app(self, argv):
        super(OpenIOShell, self).initialize_app(argv)

        for module in clientmanager.PLUGIN_MODULES:
            api = module.API_NAME
            cmd_group = 'openio.' + api.replace('-', '_')
            self.command_manager.add_command_group(cmd_group)
            self.log.debug(
                '%s API: cmd group %s' % (api, cmd_group)
            )
        self.command_manager.add_command_group('openio.common')
        self.command_manager.add_command_group('openio.ext')

        options = {
            'namespace': self.options.ns,
            'account_name': self.options.account_name,
            'proxyd_url': self.options.proxyd_url,
            'admin_mode': self.options.admin_mode,
            'log_level': logging.getLevelName(
                logging.getLogger('').getEffectiveLevel()),
            'is_cli': True,
        }

        self.print_help_if_requested()
        self.client_manager = clientmanager.ClientManager(options)