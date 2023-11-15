    def __init__(self, opts):
        super(MinionManager, self).__init__(opts)
        self.auth_wait = self.opts['acceptance_wait_time']
        self.max_auth_wait = self.opts['acceptance_wait_time_max']
        self.minions = []
        self.jid_queue = []

        install_zmq()
        self.io_loop = ZMQDefaultLoop.current()
        self.process_manager = ProcessManager(name='MultiMinionProcessManager')
        self.io_loop.spawn_callback(self.process_manager.run, **{'asynchronous': True})  # Tornado backward compat