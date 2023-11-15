    def __init__(self, http_host, http_port, redis_address, redis_password,
                 log_dir):
        # NodeInfoGcsService
        self._gcs_node_info_stub = None
        self._gcs_rpc_error_counter = 0
        # Public attributes are accessible for all head modules.
        self.http_host = http_host
        self.http_port = http_port
        self.redis_address = dashboard_utils.address_tuple(redis_address)
        self.redis_password = redis_password
        self.log_dir = log_dir
        self.aioredis_client = None
        self.aiogrpc_gcs_channel = None
        self.http_session = None
        self.ip = ray._private.services.get_node_ip_address()
        self.server = aiogrpc.server(options=(("grpc.so_reuseport", 0), ))
        self.grpc_port = self.server.add_insecure_port("[::]:0")
        logger.info("Dashboard head grpc address: %s:%s", self.ip,
                    self.grpc_port)
        logger.info("Dashboard head http address: %s:%s", self.http_host,
                    self.http_port)