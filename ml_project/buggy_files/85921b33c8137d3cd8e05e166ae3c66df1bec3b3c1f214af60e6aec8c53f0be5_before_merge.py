    def __init__(self, interactive: bool = False, return_type: str = "python", quiet: bool = False,
                 no_file_logging: bool = False) -> None:
        """
        Initializes intelmqctl.

        Parameters:
            interactive: for cli-interface true, functions can exits, parameters are used
            return_type: 'python': no special treatment, can be used for use by other
                python code
                'text': user-friendly output for cli, default for interactive use
                'json': machine-readable output for managers
            quiet: False by default, can be activated for cron jobs etc.
            no_file_logging: do not log to the log file
        """
        self.interactive = interactive
        global RETURN_TYPE
        RETURN_TYPE = return_type
        global logger
        global QUIET
        QUIET = quiet
        self.parameters = Parameters()

        # Try to get log_level from defaults_configuration, else use default
        defaults_loading_exc = None
        try:
            self.load_defaults_configuration()
        except Exception as exc:
            defaults_loading_exc = exc
            log_level = DEFAULT_LOGGING_LEVEL
            logging_level_stream = 'DEBUG'
        else:
            log_level = self.parameters.logging_level.upper()
        # make sure that logging_level_stream is always at least INFO or more verbose
        # otherwise the output on stdout/stderr is less than the user expects
        logging_level_stream = log_level if log_level == 'DEBUG' else 'INFO'

        try:
            if no_file_logging:
                raise FileNotFoundError
            logger = utils.log('intelmqctl', log_level=log_level,
                               log_format_stream=utils.LOG_FORMAT_SIMPLE,
                               logging_level_stream=logging_level_stream)
        except (FileNotFoundError, PermissionError) as exc:
            logger = utils.log('intelmqctl', log_level=log_level, log_path=False,
                               log_format_stream=utils.LOG_FORMAT_SIMPLE,
                               logging_level_stream=logging_level_stream)
            logger.error('Not logging to file: %s', exc)
        self.logger = logger
        if defaults_loading_exc:
            self.logger.exception('Loading the defaults configuration failed!',
                                  exc_info=defaults_loading_exc)

        if not utils.drop_privileges():
            logger.warning('Running intelmqctl as root is highly discouraged!')

        APPNAME = "intelmqctl"
        try:
            VERSION = pkg_resources.get_distribution("intelmq").version
        except pkg_resources.DistributionNotFound:  # pragma: no cover
            # can only happen in interactive mode
            self.logger.error('No valid IntelMQ installation found: DistributionNotFound')
            sys.exit(1)
        DESCRIPTION = """
        description: intelmqctl is the tool to control intelmq system.

        Outputs are logged to %s/intelmqctl.log""" % DEFAULT_LOGGING_PATH
        EPILOG = '''
        intelmqctl [start|stop|restart|status|reload] --group [collectors|parsers|experts|outputs]
        intelmqctl [start|stop|restart|status|reload] bot-id
        intelmqctl [start|stop|restart|status|reload]
        intelmqctl list [bots|queues|queues-and-status]
        intelmqctl log bot-id [number-of-lines [log-level]]
        intelmqctl run bot-id message [get|pop|send]
        intelmqctl run bot-id process [--msg|--dryrun]
        intelmqctl run bot-id console
        intelmqctl clear queue-id
        intelmqctl check
        intelmqctl upgrade-config
        intelmqctl debug

Starting a bot:
    intelmqctl start bot-id
Stopping a bot:
    intelmqctl stop bot-id
Reloading a bot:
    intelmqctl reload bot-id
Restarting a bot:
    intelmqctl restart bot-id
Get status of a bot:
    intelmqctl status bot-id

Run a bot directly for debugging purpose and temporarily leverage the logging level to DEBUG:
    intelmqctl run bot-id
Get a pdb (or ipdb if installed) live console.
    intelmqctl run bot-id console
See the message that waits in the input queue.
    intelmqctl run bot-id message get
See additional help for further explanation.
    intelmqctl run bot-id --help

Starting the botnet (all bots):
    intelmqctl start
    etc.

Starting a group of bots:
    intelmqctl start --group experts
    etc.

Get a list of all configured bots:
    intelmqctl list bots
If -q is given, only the IDs of enabled bots are listed line by line.

Get a list of all queues:
    intelmqctl list queues
If -q is given, only queues with more than one item are listed.

Get a list of all queues and status of the bots:
    intelmqctl list queues-and-status

Clear a queue:
    intelmqctl clear queue-id

Get logs of a bot:
    intelmqctl log bot-id number-of-lines log-level
Reads the last lines from bot log.
Log level should be one of DEBUG, INFO, ERROR or CRITICAL.
Default is INFO. Number of lines defaults to 10, -1 gives all. Result
can be longer due to our logging format!

Upgrade from a previous version:
    intelmqctl upgrade-config
Make a backup of your configuration first, also including bot's configuration files.

Get some debugging output on the settings and the enviroment (to be extended):
    intelmqctl debug --get-paths
    intelmqctl debug --get-environment-variables
'''

        # stolen functions from the bot file
        # this will not work with various instances of REDIS
        try:
            self.pipeline_configuration = utils.load_configuration(PIPELINE_CONF_FILE)
        except ValueError as exc:  # pragma: no cover
            self.abort('Error loading %r: %s' % (PIPELINE_CONF_FILE, exc))

        try:
            self.runtime_configuration = utils.load_configuration(RUNTIME_CONF_FILE)
        except ValueError as exc:  # pragma: no cover
            self.abort('Error loading %r: %s' % (RUNTIME_CONF_FILE, exc))

        process_manager = getattr(self.parameters, 'process_manager', 'intelmq')
        if process_manager not in PROCESS_MANAGER:
            self.abort('Invalid process manager given: %r, should be one of %r.'
                       '' % (process_manager, list(PROCESS_MANAGER.keys())))
        self.bot_process_manager = PROCESS_MANAGER[process_manager](
            self.runtime_configuration,
            logger,
            self
        )

        if self.interactive:
            parser = argparse.ArgumentParser(
                prog=APPNAME,
                description=DESCRIPTION,
                epilog=EPILOG,
                formatter_class=argparse.RawDescriptionHelpFormatter,
            )

            parser.add_argument('-v', '--version',
                                action='version', version=VERSION)
            parser.add_argument('--type', '-t', choices=RETURN_TYPES,
                                default=RETURN_TYPES[0],
                                help='choose if it should return regular text '
                                     'or other machine-readable')

            parser.add_argument('--quiet', '-q', action='store_true',
                                help='Quiet mode, useful for reloads initiated '
                                     'scripts like logrotate')

            subparsers = parser.add_subparsers(title='subcommands')

            parser_list = subparsers.add_parser('list', help='Listing bots or queues')
            parser_list.add_argument('kind', choices=['bots', 'queues', 'queues-and-status'])
            parser_list.add_argument('--non-zero', '--quiet', '-q', action='store_true',
                                     help='Only list non-empty queues '
                                          'or the IDs of enabled bots.')
            parser_list.set_defaults(func=self.list)

            parser_clear = subparsers.add_parser('clear', help='Clear a queue')
            parser_clear.add_argument('queue', help='queue name')
            parser_clear.set_defaults(func=self.clear_queue)

            parser_log = subparsers.add_parser('log', help='Get last log lines of a bot')
            parser_log.add_argument('bot_id', help='bot id')
            parser_log.add_argument('number_of_lines', help='number of lines',
                                    default=10, type=int, nargs='?')
            parser_log.add_argument('log_level', help='logging level',
                                    choices=LOG_LEVEL.keys(), default='INFO', nargs='?')
            parser_log.set_defaults(func=self.read_bot_log)

            parser_run = subparsers.add_parser('run', help='Run a bot interactively')
            parser_run.add_argument('bot_id',
                                    choices=self.runtime_configuration.keys())
            parser_run.add_argument('--loglevel', '-l',
                                    nargs='?', default=None,
                                    choices=LOG_LEVEL.keys())
            parser_run_subparsers = parser_run.add_subparsers(title='run-subcommands')

            parser_run_console = parser_run_subparsers.add_parser('console', help='Get a ipdb live console.')
            parser_run_console.add_argument('console_type', nargs='?',
                                            help='You may specify which console should be run. Default is ipdb (if installed)'
                                                 ' or pudb (if installed) or pdb but you may want to use another one.')
            parser_run_console.set_defaults(run_subcommand="console")

            parser_run_message = parser_run_subparsers.add_parser('message',
                                                                  help='Debug bot\'s pipelines. Get the message in the'
                                                                       ' input pipeline, pop it (cut it) and display it, or'
                                                                       ' send the message directly to bot\'s output pipeline(s).')
            parser_run_message.add_argument('message_action_kind',
                                            choices=["get", "pop", "send"],
                                            help='get: show the next message in the source pipeline. '
                                                 'pop: show and delete the next message in the source pipeline '
                                                 'send: Send the given message to the destination pipeline(s).')
            parser_run_message.add_argument('msg', nargs='?', help='If send was chosen, put here the message in JSON.')
            parser_run_message.set_defaults(run_subcommand="message")

            parser_run_process = parser_run_subparsers.add_parser('process', help='Single run of bot\'s process() method.')
            parser_run_process.add_argument('--show-sent', '-s', action='store_true',
                                            help='If message is sent through, displays it.')
            parser_run_process.add_argument('--dryrun', '-d', action='store_true',
                                            help='Never really pop the message from the input pipeline '
                                                 'nor send to output pipeline.')
            parser_run_process.add_argument('--msg', '-m',
                                            help='Trick the bot to process this JSON '
                                                 'instead of the Message in its pipeline.')
            parser_run_process.set_defaults(run_subcommand="process")
            parser_run.set_defaults(func=self.bot_run)

            parser_check = subparsers.add_parser('check',
                                                 help='Check installation and configuration')
            parser_check.add_argument('--quiet', '-q', action='store_true',
                                      help='Only print warnings and errors.')
            parser_check.add_argument('--no-connections', '-C', action='store_true',
                                      help='Do not test the connections to services like redis.')
            parser_check.set_defaults(func=self.check)

            parser_help = subparsers.add_parser('help',
                                                help='Show the help')
            parser_help.set_defaults(func=parser.print_help)

            parser_start = subparsers.add_parser('start', help='Start a bot or botnet')
            parser_start.add_argument('bot_id', nargs='?',
                                      choices=self.runtime_configuration.keys())
            parser_start.add_argument('--group', help='Start a group of bots',
                                      choices=BOT_GROUP.keys())
            parser_start.set_defaults(func=self.bot_start)

            parser_stop = subparsers.add_parser('stop', help='Stop a bot or botnet')
            parser_stop.add_argument('bot_id', nargs='?',
                                     choices=self.runtime_configuration.keys())
            parser_stop.add_argument('--group', help='Stop a group of bots',
                                     choices=BOT_GROUP.keys())
            parser_stop.set_defaults(func=self.bot_stop)

            parser_restart = subparsers.add_parser('restart', help='Restart a bot or botnet')
            parser_restart.add_argument('bot_id', nargs='?',
                                        choices=self.runtime_configuration.keys())
            parser_restart.add_argument('--group', help='Restart a group of bots',
                                        choices=BOT_GROUP.keys())
            parser_restart.set_defaults(func=self.bot_restart)

            parser_reload = subparsers.add_parser('reload', help='Reload a bot or botnet')
            parser_reload.add_argument('bot_id', nargs='?',
                                       choices=self.runtime_configuration.keys())
            parser_reload.add_argument('--group', help='Reload a group of bots',
                                       choices=BOT_GROUP.keys())
            parser_reload.set_defaults(func=self.bot_reload)

            parser_status = subparsers.add_parser('status', help='Status of a bot or botnet')
            parser_status.add_argument('bot_id', nargs='?',
                                       choices=self.runtime_configuration.keys())
            parser_status.add_argument('--group', help='Get status of a group of bots',
                                       choices=BOT_GROUP.keys())
            parser_status.set_defaults(func=self.bot_status)

            parser_status = subparsers.add_parser('enable', help='Enable a bot')
            parser_status.add_argument('bot_id',
                                       choices=self.runtime_configuration.keys())
            parser_status.set_defaults(func=self.bot_enable)

            parser_status = subparsers.add_parser('disable', help='Disable a bot')
            parser_status.add_argument('bot_id',
                                       choices=self.runtime_configuration.keys())
            parser_status.set_defaults(func=self.bot_disable)

            parser_upgrade_conf = subparsers.add_parser('upgrade-config',
                                                        help='Upgrade IntelMQ configuration to a newer version.')
            parser_upgrade_conf.add_argument('-p', '--previous',
                                             help='Use this version as the previous one.')
            parser_upgrade_conf.add_argument('-d', '--dry-run',
                                             action='store_true', default=False,
                                             help='Do not write any files.')
            parser_upgrade_conf.add_argument('-u', '--function',
                                             help='Run this upgrade function.',
                                             choices=upgrades.__all__)
            parser_upgrade_conf.add_argument('-f', '--force',
                                             action='store_true',
                                             help='Force running the upgrade procedure.')
            parser_upgrade_conf.add_argument('--state-file',
                                             help='The state file location to use.',
                                             default=STATE_FILE_PATH)
            parser_upgrade_conf.add_argument('--no-backup',
                                             help='Do not create backups of state and configuration files.',
                                             action='store_true')
            parser_upgrade_conf.set_defaults(func=self.upgrade_conf)

            parser_debug = subparsers.add_parser('debug', help='Get debugging output.')
            parser_debug.add_argument('--get-paths', help='Give all paths',
                                      action='append_const', dest='sections',
                                      const='paths')
            parser_debug.add_argument('--get-environment-variables',
                                      help='Give environment variables',
                                      action='append_const', dest='sections',
                                      const='environment_variables')
            parser_debug.set_defaults(func=self.debug)

            self.parser = parser