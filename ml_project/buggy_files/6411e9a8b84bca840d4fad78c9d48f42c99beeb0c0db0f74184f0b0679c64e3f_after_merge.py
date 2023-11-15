    def __init__(self, opts, timeout=60, safe=True, loaded_base_name=None, io_loop=None, jid_queue=None):  # pylint: disable=W0231
        '''
        Pass in the options dict
        '''
        # this means that the parent class doesn't know *which* master we connect to
        super(Minion, self).__init__(opts)
        self.timeout = timeout
        self.safe = safe

        self._running = None
        self.win_proc = []
        self.loaded_base_name = loaded_base_name
        self.connected = False
        self.restart = False
        # Flag meaning minion has finished initialization including first connect to the master.
        # True means the Minion is fully functional and ready to handle events.
        self.ready = False
        self.jid_queue = [] if jid_queue is None else jid_queue
        self.periodic_callbacks = {}

        if io_loop is None:
            install_zmq()
            self.io_loop = ZMQDefaultLoop.current()
        else:
            self.io_loop = io_loop

        # Warn if ZMQ < 3.2
        if zmq:
            if ZMQ_VERSION_INFO < (3, 2):
                log.warning(
                    'You have a version of ZMQ less than ZMQ 3.2! There are '
                    'known connection keep-alive issues with ZMQ < 3.2 which '
                    'may result in loss of contact with minions. Please '
                    'upgrade your ZMQ!'
                )
        # Late setup of the opts grains, so we can log from the grains
        # module.  If this is a proxy, however, we need to init the proxymodule
        # before we can get the grains.  We do this for proxies in the
        # post_master_init
        if not salt.utils.platform.is_proxy():
            self.opts['grains'] = salt.loader.grains(opts)
        else:
            if self.opts.get('beacons_before_connect', False):
                log.warning(
                    '\'beacons_before_connect\' is not supported '
                    'for proxy minions. Setting to False'
                )
                self.opts['beacons_before_connect'] = False
            if self.opts.get('scheduler_before_connect', False):
                log.warning(
                    '\'scheduler_before_connect\' is not supported '
                    'for proxy minions. Setting to False'
                )
                self.opts['scheduler_before_connect'] = False

        log.info('Creating minion process manager')

        if self.opts['random_startup_delay']:
            sleep_time = random.randint(0, self.opts['random_startup_delay'])
            log.info(
                'Minion sleeping for %s seconds due to configured '
                'startup_delay between 0 and %s seconds',
                sleep_time, self.opts['random_startup_delay']
            )
            time.sleep(sleep_time)

        self.process_manager = ProcessManager(name='MinionProcessManager')
        self.io_loop.spawn_callback(self.process_manager.run, **{'asynchronous': True})
        # We don't have the proxy setup yet, so we can't start engines
        # Engines need to be able to access __proxy__
        if not salt.utils.platform.is_proxy():
            self.io_loop.spawn_callback(salt.engines.start_engines, self.opts,
                                        self.process_manager)

        # Install the SIGINT/SIGTERM handlers if not done so far
        if signal.getsignal(signal.SIGINT) is signal.SIG_DFL:
            # No custom signal handling was added, install our own
            signal.signal(signal.SIGINT, self._handle_signals)

        if signal.getsignal(signal.SIGTERM) is signal.SIG_DFL:
            # No custom signal handling was added, install our own
            signal.signal(signal.SIGTERM, self._handle_signals)