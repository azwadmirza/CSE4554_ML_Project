    def _mixin_after_parsed(self):
        if len(self.args) <= 1 and not self.options.doc and not self.options.preview_target:
            try:
                self.print_help()
            except Exception:  # pylint: disable=broad-except
                # We get an argument that Python's optparser just can't deal
                # with. Perhaps stdout was redirected, or a file glob was
                # passed in. Regardless, we're in an unknown state here.
                sys.stdout.write('Invalid options passed. Please try -h for '
                                 'help.')  # Try to warn if we can.
                sys.exit(salt.defaults.exitcodes.EX_GENERIC)

        # Dump the master configuration file, exit normally at the end.
        if self.options.config_dump:
            cfg = config.master_config(self.get_config_file_path())
            sys.stdout.write(
                yaml.dump(
                    cfg,
                    default_flow_style=False,
                    Dumper=SafeOrderedDumper
                )
            )
            sys.exit(salt.defaults.exitcodes.EX_OK)

        if self.options.preview_target:
            # Insert dummy arg which won't be used
            self.args.append('not_a_valid_command')

        if self.options.doc:
            # Include the target
            if not self.args:
                self.args.insert(0, '*')
            if len(self.args) < 2:
                # Include the function
                self.args.insert(1, 'sys.doc')
            if self.args[1] != 'sys.doc':
                self.args.insert(1, 'sys.doc')
            if len(self.args) > 3:
                self.error('You can only get documentation for one method at one time.')

        if self.options.list:
            try:
                if ',' in self.args[0]:
                    self.config['tgt'] = self.args[0].replace(' ', '').split(',')
                else:
                    self.config['tgt'] = self.args[0].split()
            except IndexError:
                self.exit(42, '\nCannot execute command without defining a target.\n\n')
        else:
            try:
                self.config['tgt'] = self.args[0]
            except IndexError:
                self.exit(42, '\nCannot execute command without defining a target.\n\n')
        # Detect compound command and set up the data for it
        if self.args:
            try:
                if ',' in self.args[1]:
                    self.config['fun'] = self.args[1].split(',')
                    self.config['arg'] = [[]]
                    cmd_index = 0
                    if (self.args[2:].count(self.options.args_separator) ==
                            len(self.config['fun']) - 1):
                        # new style parsing: standalone argument separator
                        for arg in self.args[2:]:
                            if arg == self.options.args_separator:
                                cmd_index += 1
                                self.config['arg'].append([])
                            else:
                                self.config['arg'][cmd_index].append(arg)
                    else:
                        # old style parsing: argument separator can be inside args
                        for arg in self.args[2:]:
                            if self.options.args_separator in arg:
                                sub_args = arg.split(self.options.args_separator)
                                for sub_arg_index, sub_arg in enumerate(sub_args):
                                    if sub_arg:
                                        self.config['arg'][cmd_index].append(sub_arg)
                                    if sub_arg_index != len(sub_args) - 1:
                                        cmd_index += 1
                                        self.config['arg'].append([])
                            else:
                                self.config['arg'][cmd_index].append(arg)
                        if len(self.config['fun']) != len(self.config['arg']):
                            self.exit(42, 'Cannot execute compound command without '
                                          'defining all arguments.\n')
                    # parse the args and kwargs before sending to the publish
                    # interface
                    for i in range(len(self.config['arg'])):
                        self.config['arg'][i] = salt.utils.args.parse_input(
                            self.config['arg'][i])
                else:
                    self.config['fun'] = self.args[1]
                    self.config['arg'] = self.args[2:]
                    # parse the args and kwargs before sending to the publish
                    # interface
                    self.config['arg'] = \
                        salt.utils.args.parse_input(self.config['arg'])
            except IndexError:
                self.exit(42, '\nIncomplete options passed.\n\n')