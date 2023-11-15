    def parse_args(self, parser, argv, environ=None):
        environ = environ or os.environ
        args = parser.parse_args(argv)

        args.advertise = args.advertise or environ.get('MARS_CONTAINER_IP')
        load_modules = []
        for mods in tuple(args.load_modules or ()) + (environ.get('MARS_LOAD_MODULES'),):
            load_modules.extend(mods.split(',') if mods else [])
        load_modules.extend(['mars.executor', 'mars.serialize.protos'])
        args.load_modules = tuple(load_modules)

        if 'MARS_TASK_DETAIL' in environ:
            task_detail = json.loads(environ['MARS_TASK_DETAIL'])
            task_type, task_index = task_detail['task']['type'], task_detail['task']['index']

            args.advertise = args.advertise or task_detail['cluster'][task_type][task_index]
            args.schedulers = args.schedulers or ','.join(task_detail['cluster']['scheduler'])
        return args