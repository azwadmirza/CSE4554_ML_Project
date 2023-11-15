    def _mixin_after_parsed(self):
        if not self.args:
            self.print_help()
            self.error('Insufficient arguments')

        if self.options.list:
            if ',' in self.args[0]:
                self.config['tgt'] = self.args[0].split(',')
            else:
                self.config['tgt'] = self.args[0].split()
        else:
            self.config['tgt'] = self.args[0]

        self.config['argv'] = self.args[1:]
        if not self.config['argv'] or not self.config['tgt']:
            self.print_help()
            self.error('Insufficient arguments')

        # Add back the --no-parse options so that shimmed/wrapped commands
        # handle the arguments correctly.
        if self.options.no_parse:
            self.config['argv'].append(
                '--no-parse=' + ','.join(self.options.no_parse))

        if self.options.ssh_askpass:
            self.options.ssh_passwd = getpass.getpass('Password: ')
            for group in self.option_groups:
                for option in group.option_list:
                    if option.dest == 'ssh_passwd':
                        option.explicit = True
                        break