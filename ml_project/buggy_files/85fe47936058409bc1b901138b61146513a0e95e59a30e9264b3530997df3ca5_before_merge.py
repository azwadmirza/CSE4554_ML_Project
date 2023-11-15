    def __init__(self):
        global RETURN_TYPE
        global logger
        logger = utils.log('intelmqctl', log_level='DEBUG')
        self.logger = logger
        if os.geteuid() == 0:
            logger.warning('Running intelmq as root is highly discouraged!')

        APPNAME = "intelmqctl"
        VERSION = pkg_resources.get_distribution("intelmq").version
        DESCRIPTION = """
        description: intelmqctl is the tool to control intelmq system.

        Outputs are logged to /opt/intelmq/var/log/intelmqctl"""
        USAGE = '''
        intelmqctl [start|stop|restart|status|run] bot-id
        intelmqctl [start|stop|restart|status]
        intelmqctl list [bots|queues]
        intelmqctl log bot-id [number-of-lines [log-level]]
        intelmqctl clear queue-id

Starting a bot:
    intelmqctl start bot-id
Stopping a bot:
    intelmqctl stop bot-id
Restarting a bot:
    intelmqctl restart bot-id
Get status of a bot:
    intelmqctl status bot-id

Run a bot directly (blocking) for debugging purpose:
    intelmqctl run bot-id

Starting the botnet (all bots):
    intelmqctl start
    etc.

Get a list of all configured bots:
    intelmqctl list bots

Get a list of all queues:
    intelmqctl list queues

Clear a queue:
    intelmqctl clear queue-id

Get logs of a bot:
    intelmqctl log bot-id [number-of-lines [log-level]]
    Reads the last lines from bot log, or from system log if no bot ID was
    given. Log level should be one of DEBUG, INFO, ERROR or CRITICAL.
    Default is INFO. Number of lines defaults to 10, -1 gives all. Result
    can be longer due to our logging format!'''

        parser = argparse.ArgumentParser(
            prog=APPNAME,
            usage=USAGE,
            epilog=DESCRIPTION
        )

        parser.add_argument('-v', '--version',
                            action='version', version=VERSION)
        parser.add_argument('--type', '-t', choices=RETURN_TYPES,
                            default=RETURN_TYPES[0],
                            help='choose if it should return regular text or '
                                 'other machine-readable')

        parser.add_argument('action',
                            choices=['start', 'stop', 'restart', 'status',
                                     'run', 'list', 'clear', 'help', 'log'],
                            metavar='[start|stop|restart|status|run|list|clear'
                                    '|log]')
        parser.add_argument('parameter', nargs='*')
        self.args = parser.parse_args()
        if self.args.action == 'help':
            parser.print_help()
            exit(0)

        RETURN_TYPE = self.args.type

        with open(STARTUP_CONF_FILE, 'r') as fp:
            self.startup = json.load(fp)

        with open(SYSTEM_CONF_FILE, 'r') as fp:
            self.system = json.load(fp)

        if not os.path.exists(PIDDIR):
            os.makedirs(PIDDIR)

        # stolen functions from the bot file
        # this will not work with various instances of REDIS
        self.parameters = Parameters()
        self.load_defaults_configuration()
        self.load_system_configuration()
        self.pipepline_configuration = utils.load_configuration(
            PIPELINE_CONF_FILE)
        self.runtime_configuration = utils.load_configuration(
            RUNTIME_CONF_FILE)
        self.startup_configuration = utils.load_configuration(
            STARTUP_CONF_FILE)