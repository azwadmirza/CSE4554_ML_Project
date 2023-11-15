    def init(self):
        eventlet.monkey_patch(os=False)
        self.tube = self.conf.get("tube", DEFAULT_TUBE)
        self.session = requests.Session()
        self.cs = ConscienceClient(self.conf)
        self.rdir = RdirClient(self.conf)
        self._acct_addr = None
        self.acct_update = 0
        self.graceful_timeout = 1
        self.acct_refresh_interval = int_value(
            self.conf.get('acct_refresh_interval'), 60
        )
        self.acct_update = true_value(self.conf.get('acct_update', True))
        self.rdir_update = true_value(self.conf.get('rdir_update', True))
        if 'handlers_conf' not in self.conf:
            raise ValueError("'handlers_conf' path not defined in conf")
        self.handlers = loadhandlers(self.conf.get('handlers_conf'),
                                     evt_types,
                                     global_conf=self.conf,
                                     app=self)
        super(EventWorker, self).init()