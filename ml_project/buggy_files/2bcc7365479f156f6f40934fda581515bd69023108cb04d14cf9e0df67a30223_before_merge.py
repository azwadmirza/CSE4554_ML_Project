    def __init__(self,
                 influx_server: str,
                 influx_user: str,
                 influx_password: str,
                 influx_database: str,
                 host: str,
                 port: int,
                 protocol: str,
                 reporting_frequency: int):
        self._influx_server = influx_server
        self._reporting_frequency = reporting_frequency
        self._registry = HostMetricsRegistry(host)
        self._reporter = InfluxReporter(
            registry=self._registry,
            database=influx_database,
            username=influx_user,
            password=influx_password,
            protocol=protocol,
            port=port,
            server=influx_server
        )