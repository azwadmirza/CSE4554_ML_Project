    def execute(self, unexpanded_argv): # pylint: disable=too-many-statements
        argv = Application._expand_file_prefixed_files(unexpanded_argv)
        command_table = self.configuration.get_command_table()
        self.raise_event(self.COMMAND_TABLE_LOADED, command_table=command_table)
        self.parser.load_command_table(command_table)
        self.raise_event(self.COMMAND_PARSER_LOADED, parser=self.parser)

        if len(argv) == 0:
            enable_autocomplete(self.parser)
            az_subparser = self.parser.subparsers[tuple()]
            _help.show_welcome(az_subparser)
            log_telemetry('welcome')
            return None

        if argv[0].lower() == 'help':
            argv[0] = '--help'

        # Rudimentary parsing to get the command
        nouns = []
        for noun in argv:
            try:
                if noun[0] == '-':
                    break
            except IndexError:
                pass
            nouns.append(noun)
        command = ' '.join(nouns)

        if argv[-1] in ('--help', '-h') or command in command_table:
            self.configuration.load_params(command)
            self.raise_event(self.COMMAND_TABLE_PARAMS_LOADED, command_table=command_table)
            self.parser.load_command_table(command_table)

        if self.session['completer_active']:
            enable_autocomplete(self.parser)

        args = self.parser.parse_args(argv)

        self.raise_event(self.COMMAND_PARSER_PARSED, command=args.command, args=args)
        results = []
        for expanded_arg in _explode_list_args(args):
            self.session['command'] = expanded_arg.command
            try:
                _validate_arguments(expanded_arg)
            except CLIError:
                raise
            except: # pylint: disable=bare-except
                err = sys.exc_info()[1]
                getattr(expanded_arg, '_parser', self.parser).validation_error(str(err))

            # Consider - we are using any args that start with an underscore (_) as 'private'
            # arguments and remove them from the arguments that we pass to the actual function.
            # This does not feel quite right.
            params = dict([(key, value)
                           for key, value in expanded_arg.__dict__.items()
                           if not key.startswith('_')])
            params.pop('subcommand', None)
            params.pop('func', None)
            params.pop('command', None)
            log_telemetry(expanded_arg.command, log_type='pageview',
                          output_type=self.configuration.output_format,
                          parameters=[p for p in unexpanded_argv if p.startswith('-')])

            result = expanded_arg.func(params)
            result = todict(result)
            results.append(result)

        if len(results) == 1:
            results = results[0]

        event_data = {'result': results}
        self.raise_event(self.TRANSFORM_RESULT, event_data=event_data)
        self.raise_event(self.FILTER_RESULT, event_data=event_data)
        return CommandResultItem(event_data['result'],
                                 table_transformer=
                                 command_table[args.command].table_transformer,
                                 is_query_active=self.session['query_active'])