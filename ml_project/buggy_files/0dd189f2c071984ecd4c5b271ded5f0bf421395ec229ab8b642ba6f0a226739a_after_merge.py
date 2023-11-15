    def main(self):
        if not os.path.exists(self.config.config['molecule']['molecule_dir']):
            os.makedirs(self.config.config['molecule']['molecule_dir'])

        self.state = state.State(
            state_file=self.config.config.get('molecule').get('state_file'))

        try:
            self.driver = self._get_driver()
        except basedriver.InvalidDriverSpecified:
            LOG.error("Invalid driver '{}'".format(self._get_driver_name()))
            # TODO(retr0h): Print valid drivers.
            util.sysexit()
        except basedriver.InvalidProviderSpecified:
            LOG.error("Invalid provider '{}'".format(self.args['provider']))
            self.args['provider'] = None
            self.args['platform'] = None
            self.driver = self._get_driver()
            self.print_valid_providers()
            util.sysexit()
        except basedriver.InvalidPlatformSpecified:
            LOG.error("Invalid platform '{}'".format(self.args['platform']))
            self.args['provider'] = None
            self.args['platform'] = None
            self.driver = self._get_driver()
            self.print_valid_platforms()
            util.sysexit()

        # updates instances config with full machine names
        self.config.populate_instance_names(self.driver.platform)

        if self.args.get('debug'):
            util.print_debug(
                'RUNNING CONFIG',
                yaml.dump(
                    self.config.config, default_flow_style=False, indent=2))

        self._add_or_update_vars('group_vars')
        self._add_or_update_vars('host_vars')