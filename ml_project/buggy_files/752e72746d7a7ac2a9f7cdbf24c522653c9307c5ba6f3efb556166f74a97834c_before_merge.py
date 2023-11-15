    def __init__(self,
                 ray_params,
                 head=False,
                 shutdown_at_exit=True,
                 spawn_reaper=True,
                 connect_only=False):
        """Start a node.

        Args:
            ray_params (ray.params.RayParams): The parameters to use to
                configure the node.
            head (bool): True if this is the head node, which means it will
                start additional processes like the Redis servers, monitor
                processes, and web UI.
            shutdown_at_exit (bool): If true, spawned processes will be cleaned
                up if this process exits normally.
            spawn_reaper (bool): If true, spawns a process that will clean up
                other spawned processes if this process dies unexpectedly.
            connect_only (bool): If true, connect to the node without starting
                new processes.
        """
        if shutdown_at_exit:
            if connect_only:
                raise ValueError("'shutdown_at_exit' and 'connect_only' "
                                 "cannot both be true.")
            self._register_shutdown_hooks()

        self.head = head
        self.kernel_fate_share = bool(
            spawn_reaper and ray.utils.detect_fate_sharing_support())
        self.all_processes = {}

        # Try to get node IP address with the parameters.
        if ray_params.node_ip_address:
            node_ip_address = ray_params.node_ip_address
        elif ray_params.redis_address:
            node_ip_address = ray.services.get_node_ip_address(
                ray_params.redis_address)
        else:
            node_ip_address = ray.services.get_node_ip_address()
        self._node_ip_address = node_ip_address

        if ray_params.raylet_ip_address:
            raylet_ip_address = ray_params.raylet_ip_address
        else:
            raylet_ip_address = node_ip_address

        if raylet_ip_address != node_ip_address and (not connect_only or head):
            raise ValueError(
                "The raylet IP address should only be different than the node "
                "IP address when connecting to an existing raylet; i.e., when "
                "head=False and connect_only=True.")

        self._raylet_ip_address = raylet_ip_address

        ray_params.update_if_absent(
            include_log_monitor=True,
            resources={},
            temp_dir=ray.utils.get_ray_temp_dir(),
            worker_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "workers/default_worker.py"))

        self._resource_spec = None
        self._localhost = socket.gethostbyname("localhost")
        self._ray_params = ray_params
        self._redis_address = ray_params.redis_address
        self._config = ray_params._internal_config

        if head:
            redis_client = None
            # date including microsecond
            date_str = datetime.datetime.today().strftime(
                "%Y-%m-%d_%H-%M-%S_%f")
            self.session_name = "session_{date_str}_{pid}".format(
                pid=os.getpid(), date_str=date_str)
        else:
            redis_client = self.create_redis_client()
            self.session_name = ray.utils.decode(
                redis_client.get("session_name"))

        self._init_temp(redis_client)

        if connect_only:
            # Get socket names from the configuration.
            self._plasma_store_socket_name = (
                ray_params.plasma_store_socket_name)
            self._raylet_socket_name = ray_params.raylet_socket_name

            # If user does not provide the socket name, get it from Redis.
            if (self._plasma_store_socket_name is None
                    or self._raylet_socket_name is None
                    or self._ray_params.node_manager_port is None):
                # Get the address info of the processes to connect to
                # from Redis.
                address_info = ray.services.get_address_info_from_redis(
                    self.redis_address,
                    self._raylet_ip_address,
                    redis_password=self.redis_password)
                self._plasma_store_socket_name = address_info[
                    "object_store_address"]
                self._raylet_socket_name = address_info["raylet_socket_name"]
                self._ray_params.node_manager_port = address_info[
                    "node_manager_port"]
        else:
            # If the user specified a socket name, use it.
            self._plasma_store_socket_name = self._prepare_socket_file(
                self._ray_params.plasma_store_socket_name,
                default_prefix="plasma_store")
            self._raylet_socket_name = self._prepare_socket_file(
                self._ray_params.raylet_socket_name, default_prefix="raylet")

        if head:
            ray_params.update_if_absent(num_redis_shards=1)
            self._webui_url = None
        else:
            self._webui_url = (
                ray.services.get_webui_url_from_redis(redis_client))
            ray_params.include_java = (
                ray.services.include_java_from_redis(redis_client))

        if head or not connect_only:
            # We need to start a local raylet.
            if (self._ray_params.node_manager_port is None
                    or self._ray_params.node_manager_port == 0):
                # No port specified. Pick a random port for the raylet to use.
                # NOTE: There is a possible but unlikely race condition where
                # the port is bound by another process between now and when the
                # raylet starts.
                self._ray_params.node_manager_port = self._get_unused_port()

        if not connect_only and spawn_reaper and not self.kernel_fate_share:
            self.start_reaper_process()

        # Start processes.
        if head:
            self.start_head_processes()
            redis_client = self.create_redis_client()
            redis_client.set("session_name", self.session_name)
            redis_client.set("session_dir", self._session_dir)
            redis_client.set("temp_dir", self._temp_dir)

        if not connect_only:
            self.start_ray_processes()