def init(
        address=None,
        *,
        num_cpus=None,
        num_gpus=None,
        resources=None,
        object_store_memory=None,
        local_mode=False,
        ignore_reinit_error=False,
        include_dashboard=None,
        dashboard_host=ray_constants.DEFAULT_DASHBOARD_IP,
        dashboard_port=ray_constants.DEFAULT_DASHBOARD_PORT,
        job_config=None,
        configure_logging=True,
        logging_level=logging.INFO,
        logging_format=ray_constants.LOGGER_FORMAT,
        log_to_driver=True,
        # The following are unstable parameters and their use is discouraged.
        _enable_object_reconstruction=False,
        _redis_max_memory=None,
        _plasma_directory=None,
        _node_ip_address=ray_constants.NODE_DEFAULT_IP,
        _driver_object_store_memory=None,
        _memory=None,
        _redis_password=ray_constants.REDIS_DEFAULT_PASSWORD,
        _java_worker_options=None,
        _code_search_path=None,
        _temp_dir=None,
        _load_code_from_local=False,
        _lru_evict=False,
        _metrics_export_port=None,
        _object_spilling_config=None,
        _system_config=None):
    """
    Connect to an existing Ray cluster or start one and connect to it.

    This method handles two cases; either a Ray cluster already exists and we
    just attach this driver to it or we start all of the processes associated
    with a Ray cluster and attach to the newly started cluster.

    To start Ray and all of the relevant processes, use this as follows:

    .. code-block:: python

        ray.init()

    To connect to an existing Ray cluster, use this as follows (substituting
    in the appropriate address):

    .. code-block:: python

        ray.init(address="123.45.67.89:6379")

    You can also define an environment variable called `RAY_ADDRESS` in
    the same format as the `address` parameter to connect to an existing
    cluster with ray.init().

    Args:
        address (str): The address of the Ray cluster to connect to. If
            this address is not provided, then this command will start Redis,
            a raylet, a plasma store, a plasma manager, and some workers.
            It will also kill these processes when Python exits. If the driver
            is running on a node in a Ray cluster, using `auto` as the value
            tells the driver to detect the the cluster, removing the need to
            specify a specific node address.
        num_cpus (int): Number of CPUs the user wishes to assign to each
            raylet. By default, this is set based on virtual cores.
        num_gpus (int): Number of GPUs the user wishes to assign to each
            raylet. By default, this is set based on detected GPUs.
        resources: A dictionary mapping the names of custom resources to the
            quantities for them available.
        object_store_memory: The amount of memory (in bytes) to start the
            object store with. By default, this is automatically set based on
            available system memory.
        local_mode (bool): If true, the code will be executed serially. This
            is useful for debugging.
        ignore_reinit_error: If true, Ray suppresses errors from calling
            ray.init() a second time. Ray won't be restarted.
        include_dashboard: Boolean flag indicating whether or not to start the
            Ray dashboard, which displays the status of the Ray
            cluster. If this argument is None, then the UI will be started if
            the relevant dependencies are present.
        dashboard_host: The host to bind the dashboard server to. Can either be
            localhost (127.0.0.1) or 0.0.0.0 (available from all interfaces).
            By default, this is set to localhost to prevent access from
            external machines.
        dashboard_port: The port to bind the dashboard server to. Defaults to
            8265.
        job_config (ray.job_config.JobConfig): The job configuration.
        configure_logging: True (default) if configuration of logging is
            allowed here. Otherwise, the user may want to configure it
            separately.
        logging_level: Logging level, defaults to logging.INFO. Ignored unless
            "configure_logging" is true.
        logging_format: Logging format, defaults to string containing a
            timestamp, filename, line number, and message. See the source file
            ray_constants.py for details. Ignored unless "configure_logging"
            is true.
        log_to_driver (bool): If true, the output from all of the worker
            processes on all nodes will be directed to the driver.
        _enable_object_reconstruction (bool): If True, when an object stored in
            the distributed plasma store is lost due to node failure, Ray will
            attempt to reconstruct the object by re-executing the task that
            created the object. Arguments to the task will be recursively
            reconstructed. If False, then ray.ObjectLostError will be
            thrown.
        _redis_max_memory: Redis max memory.
        _plasma_directory: Override the plasma mmap file directory.
        _node_ip_address (str): The IP address of the node that we are on.
        _driver_object_store_memory (int): Limit the amount of memory the
            driver can use in the object store for creating objects.
        _memory: Amount of reservable memory resource to create.
        _redis_password (str): Prevents external clients without the password
            from connecting to Redis if provided.
        _temp_dir (str): If provided, specifies the root temporary
            directory for the Ray process. Defaults to an OS-specific
            conventional location, e.g., "/tmp/ray".
        _load_code_from_local: Whether code should be loaded from a local
            module or from the GCS.
        _java_worker_options: Overwrite the options to start Java workers.
        _code_search_path (list): Java classpath or python import path.
        _lru_evict (bool): If True, when an object store is full, it will evict
            objects in LRU order to make more space and when under memory
            pressure, ray.ObjectLostError may be thrown. If False, then
            reference counting will be used to decide which objects are safe
            to evict and when under memory pressure, ray.ObjectStoreFullError
            may be thrown.
        _metrics_export_port(int): Port number Ray exposes system metrics
            through a Prometheus endpoint. It is currently under active
            development, and the API is subject to change.
        _object_spilling_config (str): The configuration json string for object
            spilling I/O worker.
        _system_config (str): JSON configuration for overriding
            RayConfig defaults. For testing purposes ONLY.

    Returns:
        Address information about the started processes.

    Raises:
        Exception: An exception is raised if an inappropriate combination of
            arguments is passed in.
    """

    # Try to increase the file descriptor limit, which is too low by
    # default for Ray: https://github.com/ray-project/ray/issues/11239
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft < hard:
            logger.debug("Automatically increasing RLIMIT_NOFILE to max "
                         "value of {}".format(hard))
            try:
                resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
            except ValueError:
                logger.debug("Failed to raise limit.")
        soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft < 4096:
            logger.warning(
                "File descriptor limit {} is too low for production "
                "servers and may result in connection errors. "
                "At least 8192 is recommended. --- "
                "Fix with 'ulimit -n 8192'".format(soft))
    except ImportError:
        logger.debug("Could not import resource module (on Windows)")
        pass

    if "RAY_ADDRESS" in os.environ:
        if address is None or address == "auto":
            address = os.environ["RAY_ADDRESS"]
        else:
            raise RuntimeError(
                "Cannot use both the RAY_ADDRESS environment variable and "
                "the address argument of ray.init simultaneously. If you "
                "use RAY_ADDRESS to connect to a specific Ray cluster, "
                "please call ray.init() or ray.init(address=\"auto\") on the "
                "driver.")

    # Convert hostnames to numerical IP address.
    if _node_ip_address is not None:
        node_ip_address = services.address_to_ip(_node_ip_address)
    raylet_ip_address = node_ip_address

    if address:
        redis_address, _, _ = services.validate_redis_address(address)
    else:
        redis_address = None

    if configure_logging:
        setup_logger(logging_level, logging_format)

    if redis_address is not None:
        logger.info(
            f"Connecting to existing Ray cluster at address: {redis_address}")

    if local_mode:
        driver_mode = LOCAL_MODE
    else:
        driver_mode = SCRIPT_MODE

    if global_worker.connected:
        if ignore_reinit_error:
            logger.error("Calling ray.init() again after it has already been "
                         "called.")
            return
        else:
            raise RuntimeError("Maybe you called ray.init twice by accident? "
                               "This error can be suppressed by passing in "
                               "'ignore_reinit_error=True' or by calling "
                               "'ray.shutdown()' prior to 'ray.init()'.")

    _system_config = _system_config or {}
    if not isinstance(_system_config, dict):
        raise TypeError("The _system_config must be a dict.")

    global _global_node
    if redis_address is None:
        # In this case, we need to start a new cluster.
        ray_params = ray.parameter.RayParams(
            redis_address=redis_address,
            node_ip_address=node_ip_address,
            raylet_ip_address=raylet_ip_address,
            object_ref_seed=None,
            driver_mode=driver_mode,
            redirect_worker_output=None,
            redirect_output=None,
            num_cpus=num_cpus,
            num_gpus=num_gpus,
            resources=resources,
            num_redis_shards=None,
            redis_max_clients=None,
            redis_password=_redis_password,
            plasma_directory=_plasma_directory,
            huge_pages=None,
            include_dashboard=include_dashboard,
            dashboard_host=dashboard_host,
            dashboard_port=dashboard_port,
            memory=_memory,
            object_store_memory=object_store_memory,
            redis_max_memory=_redis_max_memory,
            plasma_store_socket_name=None,
            temp_dir=_temp_dir,
            load_code_from_local=_load_code_from_local,
            java_worker_options=_java_worker_options,
            code_search_path=_code_search_path,
            start_initial_python_workers_for_first_job=True,
            _system_config=_system_config,
            lru_evict=_lru_evict,
            enable_object_reconstruction=_enable_object_reconstruction,
            metrics_export_port=_metrics_export_port,
            object_spilling_config=_object_spilling_config)
        # Start the Ray processes. We set shutdown_at_exit=False because we
        # shutdown the node in the ray.shutdown call that happens in the atexit
        # handler. We still spawn a reaper process in case the atexit handler
        # isn't called.
        _global_node = ray.node.Node(
            head=True,
            shutdown_at_exit=False,
            spawn_reaper=True,
            ray_params=ray_params)
    else:
        # In this case, we are connecting to an existing cluster.
        if num_cpus is not None or num_gpus is not None:
            raise ValueError(
                "When connecting to an existing cluster, num_cpus "
                "and num_gpus must not be provided.")
        if resources is not None:
            raise ValueError("When connecting to an existing cluster, "
                             "resources must not be provided.")
        if object_store_memory is not None:
            raise ValueError("When connecting to an existing cluster, "
                             "object_store_memory must not be provided.")
        if _system_config is not None and len(_system_config) != 0:
            raise ValueError("When connecting to an existing cluster, "
                             "_system_config must not be provided.")
        if _lru_evict:
            raise ValueError("When connecting to an existing cluster, "
                             "_lru_evict must not be provided.")
        if _enable_object_reconstruction:
            raise ValueError(
                "When connecting to an existing cluster, "
                "_enable_object_reconstruction must not be provided.")

        # In this case, we only need to connect the node.
        ray_params = ray.parameter.RayParams(
            node_ip_address=node_ip_address,
            raylet_ip_address=raylet_ip_address,
            redis_address=redis_address,
            redis_password=_redis_password,
            object_ref_seed=None,
            temp_dir=_temp_dir,
            load_code_from_local=_load_code_from_local,
            _system_config=_system_config,
            lru_evict=_lru_evict,
            enable_object_reconstruction=_enable_object_reconstruction,
            metrics_export_port=_metrics_export_port)
        _global_node = ray.node.Node(
            ray_params,
            head=False,
            shutdown_at_exit=False,
            spawn_reaper=False,
            connect_only=True)

    connect(
        _global_node,
        mode=driver_mode,
        log_to_driver=log_to_driver,
        worker=global_worker,
        driver_object_store_memory=_driver_object_store_memory,
        job_id=None,
        job_config=job_config)

    for hook in _post_init_hooks:
        hook()

    node_id = global_worker.core_worker.get_current_node_id()
    return dict(_global_node.address_info, node_id=node_id.hex())