    def _main(self, argv=None):
        parser = argparse.ArgumentParser(description=self.service_description)
        parser.add_argument('-a', '--advertise', help='advertise ip')
        parser.add_argument('-k', '--kv-store', help='address of kv store service, '
                                                     'for instance, etcd://localhost:4001')
        parser.add_argument('-e', '--endpoint', help='endpoint of the service')
        parser.add_argument('-s', '--schedulers', help='endpoint of scheduler, when single scheduler '
                                                       'and etcd is not available')
        parser.add_argument('-H', '--host', help='host of the scheduler service, only available '
                                                 'when `endpoint` is absent')
        parser.add_argument('-p', '--port', help='port of the scheduler service, only available '
                                                 'when `endpoint` is absent')
        parser.add_argument('--level', help='log level')
        parser.add_argument('--format', help='log format')
        parser.add_argument('--log_conf', help='log config file')
        parser.add_argument('--inspect', help='inspection endpoint')
        parser.add_argument('--load-modules', nargs='*', help='modules to import')
        self.config_args(parser)
        args = parser.parse_args(argv)
        self.args = args

        endpoint = args.endpoint
        host = args.host
        port = args.port
        options.kv_store = args.kv_store if args.kv_store else options.kv_store

        load_modules = []
        for mod in args.load_modules or ():
            load_modules.extend(mod.split(','))
        if not args.load_modules:
            load_module_str = os.environ.get('MARS_LOAD_MODULES')
            if load_module_str:
                load_modules = load_module_str.split(',')
        load_modules.append('mars.tensor')
        [__import__(m, globals(), locals(), []) for m in load_modules]
        self.service_logger.info('Modules %s loaded', ','.join(load_modules))

        self.n_process = 1

        self.config_service()
        self.config_logging()

        if not host:
            host = args.advertise or '0.0.0.0'
        if not endpoint and port:
            endpoint = host + ':' + port

        try:
            self.validate_arguments()
        except StartArgumentError as ex:
            parser.error('Failed to start application: %s' % ex)

        if getattr(self, 'require_pool', True):
            self.endpoint, self.pool = self._try_create_pool(endpoint=endpoint, host=host, port=port)
        self.service_logger.info('%s started at %s.', self.service_description, self.endpoint)
        self.main_loop()