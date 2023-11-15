    def execute(self,
                idempotent=False,
                create_instances=True,
                create_inventory=True,
                exit=True,
                hide_errors=True):
        """
        Execute the actions necessary to perform a `molecule converge` and
        return a tuple.

        :param idempotent: An optional flag to perform the converge again, and
         parse the output for idempotence.
        :param create_inventory: An optional flag to toggle inventory creation.
        :param create_instances: An optional flag to toggle instance creation.
        :return: Return a tuple of (`exit status`, `command output`), otherwise
         sys.exit on command failure.
        """
        if self.molecule.state.created:
            create_instances = False

        if self.molecule.state.converged:
            create_inventory = False

        if self.molecule.state.multiple_platforms:
            self.command_args['platform'] = 'all'
        else:
            if ((self.command_args.get('platform') == 'all') and
                    self.molecule.state.created):
                create_instances = True
                create_inventory = True

        if create_instances and not idempotent:
            c = create.Create(self.command_args, self.args, self.molecule)
            c.execute()

        if create_inventory:
            self.molecule.create_inventory_file()

        # Install role dependencies only during `molecule converge`
        if not idempotent and 'requirements_file' in \
            self.molecule.config.config['ansible'] and not \
                self.molecule.state.installed_deps:
            galaxy = ansible_galaxy.AnsibleGalaxy(self.molecule.config.config)
            galaxy.install()
            self.molecule.state.change_state('installed_deps', True)

        ansible = ansible_playbook.AnsiblePlaybook(
            self.molecule.config.config['ansible'],
            self.molecule.driver.ansible_connection_params)

        # Target tags passed in via CLI
        if self.command_args.get('tags'):
            ansible.add_cli_arg('tags', self.command_args.get('tags'))

        if idempotent:
            # Don't log stdout/err
            ansible.remove_cli_arg('_out')
            ansible.remove_cli_arg('_err')
            # Idempotence task regexp cannot handle diff
            ansible.remove_cli_arg('diff')
            # Disable color for regexp
            ansible.add_env_arg('ANSIBLE_NOCOLOR', 'true')
            ansible.add_env_arg('ANSIBLE_FORCE_COLOR', 'false')

        ansible.bake()
        if self.args.get('debug'):
            ansible_env = {k: v
                           for (k, v) in ansible.env.items() if 'ANSIBLE' in k}
            other_env = {k: v
                         for (k, v) in ansible.env.items()
                         if 'ANSIBLE' not in k}
            util.print_debug(
                'OTHER ENVIRONMENT',
                yaml.dump(
                    other_env, default_flow_style=False, indent=2))
            util.print_debug(
                'ANSIBLE ENVIRONMENT',
                yaml.dump(
                    ansible_env, default_flow_style=False, indent=2))
            util.print_debug('ANSIBLE PLAYBOOK', str(ansible._ansible))

        util.print_info('Starting Ansible Run ...')
        status, output = ansible.execute(hide_errors=hide_errors)
        if status is not None:
            if exit:
                util.sysexit(status)
            return status, None

        if not self.molecule.state.converged:
            self.molecule.state.change_state('converged', True)

        return None, output