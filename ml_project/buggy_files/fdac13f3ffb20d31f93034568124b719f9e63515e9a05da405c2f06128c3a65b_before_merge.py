    def __init__(self, session):
        super(ResourceMonitor, self).__init__()

        self._logger = logging.getLogger(self.__class__.__name__)
        self.session = session
        self.check_interval = 5
        self.cpu_data = []
        self.memory_data = []
        self.process = psutil.Process()
        self.history_size = session.get_resource_monitor_history_size()