    def __init__(self,
                 node_ip_address,
                 redis_address,
                 dashboard_agent_port,
                 redis_password=None,
                 temp_dir=None,
                 log_dir=None,
                 metrics_export_port=None,
                 node_manager_port=None,
                 object_store_name=None,
                 raylet_name=None):
        """Initialize the DashboardAgent object."""
        # Public attributes are accessible for all agent modules.
        self.ip = node_ip_address
        self.redis_address = dashboard_utils.address_tuple(redis_address)
        self.redis_password = redis_password
        self.temp_dir = temp_dir
        self.log_dir = log_dir
        self.dashboard_agent_port = dashboard_agent_port
        self.metrics_export_port = metrics_export_port
        self.node_manager_port = node_manager_port
        self.object_store_name = object_store_name
        self.raylet_name = raylet_name
        self.node_id = os.environ["RAY_NODE_ID"]
        # TODO(edoakes): RAY_RAYLET_PID isn't properly set on Windows. This is
        # only used for fate-sharing with the raylet and we need a different
        # fate-sharing mechanism for Windows anyways.
        if sys.platform not in ["win32", "cygwin"]:
            self.ppid = int(os.environ["RAY_RAYLET_PID"])
            assert self.ppid > 0
            logger.info("Parent pid is %s", self.ppid)
        self.server = aiogrpc.server(options=(("grpc.so_reuseport", 0), ))
        self.grpc_port = self.server.add_insecure_port(
            f"[::]:{self.dashboard_agent_port}")
        logger.info("Dashboard agent grpc address: %s:%s", self.ip,
                    self.grpc_port)
        self.aioredis_client = None
        options = (("grpc.enable_http_proxy", 0), )
        self.aiogrpc_raylet_channel = aiogrpc.insecure_channel(
            f"{self.ip}:{self.node_manager_port}", options=options)
        self.http_session = None