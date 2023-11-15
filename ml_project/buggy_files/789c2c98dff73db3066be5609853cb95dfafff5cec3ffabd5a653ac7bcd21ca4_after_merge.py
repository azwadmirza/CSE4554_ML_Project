def load_config():
    '''
    Load the config from configfile and load into imported salt modules
    '''
    # Parse arguments
    parsed_args = parse_args()

    # Let's find out the path of this module
    if 'SETUP_DIRNAME' in globals():
        # This is from the exec() call in Salt's setup.py
        this_file = os.path.join(SETUP_DIRNAME, 'salt', 'syspaths.py')  # pylint: disable=E0602
    else:
        this_file = __file__
    install_dir = os.path.dirname(os.path.realpath(this_file))

    # Load unique data for Windows or Linux
    if salt.utils.platform.is_windows():
        if parsed_args.get('configfile') is None:
            parsed_args['configfile'] = 'C:\\Program Files (x86)\\Hubble\\etc\\hubble\\hubble.conf'
        salt.config.DEFAULT_MINION_OPTS['cachedir'] = 'C:\\Program Files (x86)\\hubble\\var\\cache'
        salt.config.DEFAULT_MINION_OPTS['pidfile'] = 'C:\\Program Files (x86)\\hubble\\var\\run\\hubble.pid'
        salt.config.DEFAULT_MINION_OPTS['log_file'] = 'C:\\Program Files (x86)\\hubble\\var\\log\\hubble.log'
        salt.config.DEFAULT_MINION_OPTS['osquery_dbpath'] = 'C:\\Program Files (x86)\\hubble\\var\\hubble_osquery_db'
        salt.config.DEFAULT_MINION_OPTS['osquerylogpath'] = 'C:\\Program Files (x86)\\hubble\\var\\log\\hubble_osquery'
        salt.config.DEFAULT_MINION_OPTS['osquerylog_backupdir'] = \
                                        'C:\\Program Files (x86)\\hubble\\var\\log\\hubble_osquery\\backuplogs'

    else:
        if parsed_args.get('configfile') is None:
            parsed_args['configfile'] = '/etc/hubble/hubble'
        salt.config.DEFAULT_MINION_OPTS['cachedir'] = '/var/cache/hubble'
        salt.config.DEFAULT_MINION_OPTS['pidfile'] = '/var/run/hubble.pid'
        salt.config.DEFAULT_MINION_OPTS['log_file'] = '/var/log/hubble'
        salt.config.DEFAULT_MINION_OPTS['osquery_dbpath'] = '/var/cache/hubble/osquery'
        salt.config.DEFAULT_MINION_OPTS['osquerylogpath'] = '/var/log/hubble_osquery'
        salt.config.DEFAULT_MINION_OPTS['osquerylog_backupdir'] = '/var/log/hubble_osquery/backuplogs'

    salt.config.DEFAULT_MINION_OPTS['file_roots'] = {'base': []}
    salt.config.DEFAULT_MINION_OPTS['log_level'] = 'error'
    salt.config.DEFAULT_MINION_OPTS['file_client'] = 'local'
    salt.config.DEFAULT_MINION_OPTS['fileserver_update_frequency'] = 43200  # 12 hours
    salt.config.DEFAULT_MINION_OPTS['grains_refresh_frequency'] = 3600  # 1 hour
    salt.config.DEFAULT_MINION_OPTS['scheduler_sleep_frequency'] = 0.5
    salt.config.DEFAULT_MINION_OPTS['default_include'] = 'hubble.d/*.conf'
    salt.config.DEFAULT_MINION_OPTS['logfile_maxbytes'] = 100000000 # 100MB
    salt.config.DEFAULT_MINION_OPTS['logfile_backups'] = 1 # maximum rotated logs
    salt.config.DEFAULT_MINION_OPTS['delete_inaccessible_azure_containers'] = False
    salt.config.DEFAULT_MINION_OPTS['enable_globbing_in_nebula_masking'] = False  # Globbing will not be supported in nebula masking
    salt.config.DEFAULT_MINION_OPTS['osquery_logfile_maxbytes'] = 50000000 # 50MB
    salt.config.DEFAULT_MINION_OPTS['osquery_logfile_maxbytes_toparse'] = 100000000 #100MB
    salt.config.DEFAULT_MINION_OPTS['osquery_backuplogs_count'] = 2
    

    global __opts__

    __opts__ = salt.config.minion_config(parsed_args.get('configfile'))
    __opts__.update(parsed_args)
    __opts__['conf_file'] = parsed_args.get('configfile')
    __opts__['install_dir'] = install_dir

    if __opts__['version']:
        print(__version__)
        clean_up_process(None, None)
        sys.exit(0)

    scan_proc = __opts__.get('scan_proc', False)
    if __opts__['daemonize']:
        # before becoming a daemon, check for other procs and possibly send
        # then a signal 15 (otherwise refuse to run)
        if not __opts__.get('ignore_running', False):
            check_pidfile(kill_other=True, scan_proc=scan_proc)
        salt.utils.daemonize()
        create_pidfile()
    elif not __opts__['function'] and not __opts__['version']:
        # check the pidfile and possibly refuse to run
        # (assuming this isn't a single function call)
        if not __opts__.get('ignore_running', False):
            check_pidfile(kill_other=False, scan_proc=scan_proc)

    signal.signal(signal.SIGTERM, clean_up_process)
    signal.signal(signal.SIGINT, clean_up_process)

    # Optional sleep to wait for network
    time.sleep(int(__opts__.get('startup_sleep', 0)))

    # Convert -vvv to log level
    if __opts__['log_level'] is None:
        # Default to 'error'
        __opts__['log_level'] = 'error'
        # Default to more verbose if we're daemonizing
        if __opts__['daemonize']:
            __opts__['log_level'] = 'info'
    # Handle the explicit -vvv settings
    if __opts__['verbose'] == 1:
        __opts__['log_level'] = 'warning'
    elif __opts__['verbose'] == 2:
        __opts__['log_level'] = 'info'
    elif __opts__['verbose'] >= 3:
        __opts__['log_level'] = 'debug'

    # Setup module/grain/returner dirs
    module_dirs = __opts__.get('module_dirs', [])
    module_dirs.append(os.path.join(os.path.dirname(__file__), 'extmods', 'modules'))
    __opts__['module_dirs'] = module_dirs
    grains_dirs = __opts__.get('grains_dirs', [])
    grains_dirs.append(os.path.join(os.path.dirname(__file__), 'extmods', 'grains'))
    __opts__['grains_dirs'] = grains_dirs
    returner_dirs = __opts__.get('returner_dirs', [])
    returner_dirs.append(os.path.join(os.path.dirname(__file__), 'extmods', 'returners'))
    __opts__['returner_dirs'] = returner_dirs
    fileserver_dirs = __opts__.get('fileserver_dirs', [])
    fileserver_dirs.append(os.path.join(os.path.dirname(__file__), 'extmods', 'fileserver'))
    __opts__['fileserver_dirs'] = fileserver_dirs
    utils_dirs = __opts__.get('utils_dirs', [])
    utils_dirs.append(os.path.join(os.path.dirname(__file__), 'extmods', 'utils'))
    __opts__['utils_dirs'] = utils_dirs
    fdg_dirs = __opts__.get('fdg_dirs', [])
    fdg_dirs.append(os.path.join(os.path.dirname(__file__), 'extmods', 'fdg'))
    __opts__['fdg_dirs'] = fdg_dirs
    __opts__['file_roots']['base'].insert(0, os.path.join(os.path.dirname(__file__), 'files'))
    if 'roots' not in __opts__['fileserver_backend']:
        __opts__['fileserver_backend'].append('roots')

    # Disable all of salt's boto modules, they give nothing but trouble to the loader
    disable_modules = __opts__.get('disable_modules', [])
    disable_modules.extend([
        'boto3_elasticache',
        'boto3_route53',
        'boto_apigateway',
        'boto_asg',
        'boto_cfn',
        'boto_cloudtrail',
        'boto_cloudwatch_event',
        'boto_cloudwatch',
        'boto_cognitoidentity',
        'boto_datapipeline',
        'boto_dynamodb',
        'boto_ec2',
        'boto_efs',
        'boto_elasticache',
        'boto_elasticsearch_domain',
        'boto_elb',
        'boto_elbv2',
        'boto_iam',
        'boto_iot',
        'boto_kinesis',
        'boto_kms',
        'boto_lambda',
        'boto_rds',
        'boto_route53',
        'boto_s3_bucket',
        'boto_secgroup',
        'boto_sns',
        'boto_sqs',
        'boto_vpc',
    ])
    __opts__['disable_modules'] = disable_modules

    # Console logging is probably the same, but can be different
    console_logging_opts = {
        'log_level': __opts__.get('console_log_level', __opts__['log_level']),
        'log_format': __opts__.get('console_log_format'),
        'date_format': __opts__.get('console_log_date_format'),
    }

    # remove early console logging from the handlers
    if early_log_handler in logging.root.handlers:
        logging.root.handlers.remove(early_log_handler)

    # Setup logging
    salt.log.setup.setup_console_logger(**console_logging_opts)
    salt.log.setup.setup_logfile_logger(__opts__['log_file'],
                                        __opts__['log_level'],
                                        max_bytes=__opts__.get('logfile_maxbytes', 100000000),
                                        backup_count=__opts__.get('logfile_backups', 1))

    # 384 is 0o600 permissions, written without octal for python 2/3 compat
    os.chmod(__opts__['log_file'], 384)
    os.chmod(parsed_args.get('configfile'), 384)

    refresh_grains(initial=True)

    # splunk logs below warning, above info by default
    logging.SPLUNK = int(__opts__.get('splunk_log_level', 25))
    logging.addLevelName(logging.SPLUNK, 'SPLUNK')
    def splunk(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.SPLUNK):
            self._log(logging.SPLUNK, message, args, **kwargs)
    logging.Logger.splunk = splunk
    if __salt__['config.get']('splunklogging', False):
        root_logger = logging.getLogger()
        handler = hubblestack.splunklogging.SplunkHandler()
        handler.setLevel(logging.SPLUNK)
        root_logger.addHandler(handler)
        class MockRecord(object):
            def __init__(self, message, levelname, asctime, name):
                self.message = message
                self.levelname = levelname
                self.asctime = asctime
                self.name = name
        handler.emit(MockRecord(__grains__, 'INFO', time.asctime(), 'hubblestack.grains_report'))