    def __init__(self, _id, dp_id, conf, prom_client):
        self.db = None # pylint: disable=invalid-name
        self.dbs = None
        self.dp = None # pylint: disable=invalid-name
        self.all_dps = None
        self.type = None
        self.interval = None
        self.db_type = None
        self.dps = None
        self.compress = None
        self.file = None
        self.influx_db = None
        self.influx_host = None
        self.influx_port = None
        self.influx_user = None
        self.influx_pwd = None
        self.influx_timeout = None
        self.influx_retries = None
        self.name = None
        self.prometheus_port = None
        self.prometheus_addr = None
        self.prometheus_test_thread = None
        super(WatcherConf, self).__init__(_id, dp_id, conf)
        self.name = str(self._id)
        self.prom_client = prom_client