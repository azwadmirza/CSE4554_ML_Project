def _init(address_info=None,
          start_ray_local=False,
          object_id_seed=None,
          num_workers=None,
          num_local_schedulers=None,
          driver_mode=SCRIPT_MODE,
          redirect_output=False,
          start_workers_from_local_scheduler=True,
          num_cpus=None,
          num_gpus=None,
          num_redis_shards=None):
    """Helper method to connect to an existing Ray cluster or start a new one.

    This method handles two cases. Either a Ray cluster already exists and we
    just attach this driver to it, or we start all of the processes associated
    with a Ray cluster and attach to the newly started cluster.

    Args:
        address_info (dict): A dictionary with address information for
            processes in a partially-started Ray cluster. If
            start_ray_local=True, any processes not in this dictionary will be
            started. If provided, an updated address_info dictionary will be
            returned to include processes that are newly started.
        start_ray_local (bool): If True then this will start any processes not
            already in address_info, including Redis, a global scheduler, local
            scheduler(s), object store(s), and worker(s). It will also kill
            these processes when Python exits. If False, this will attach to an
            existing Ray cluster.
        object_id_seed (int): Used to seed the deterministic generation of
            object IDs. The same value can be used across multiple runs of the
            same job in order to generate the object IDs in a consistent
            manner. However, the same ID should not be used for different jobs.
        num_workers (int): The number of workers to start. This is only
            provided if start_ray_local is True.
        num_local_schedulers (int): The number of local schedulers to start.
            This is only provided if start_ray_local is True.
        driver_mode (bool): The mode in which to start the driver. This should
            be one of ray.SCRIPT_MODE, ray.PYTHON_MODE, and ray.SILENT_MODE.
        redirect_output (bool): True if stdout and stderr for all the processes
            should be redirected to files and false otherwise.
        start_workers_from_local_scheduler (bool): If this flag is True, then
            start the initial workers from the local scheduler. Else, start
            them from Python. The latter case is for debugging purposes only.
        num_cpus: A list containing the number of CPUs the local schedulers
            should be configured with.
        num_gpus: A list containing the number of GPUs the local schedulers
            should be configured with.
        num_redis_shards: The number of Redis shards to start in addition to
            the primary Redis shard.

    Returns:
        Address information about the started processes.

    Raises:
        Exception: An exception is raised if an inappropriate combination of
            arguments is passed in.
    """
    check_main_thread()
    if driver_mode not in [SCRIPT_MODE, PYTHON_MODE, SILENT_MODE]:
        raise Exception("Driver_mode must be in [ray.SCRIPT_MODE, "
                        "ray.PYTHON_MODE, ray.SILENT_MODE].")

    # Get addresses of existing services.
    if address_info is None:
        address_info = {}
    else:
        assert isinstance(address_info, dict)
    node_ip_address = address_info.get("node_ip_address")
    redis_address = address_info.get("redis_address")

    # Start any services that do not yet exist.
    if driver_mode == PYTHON_MODE:
        # If starting Ray in PYTHON_MODE, don't start any other processes.
        pass
    elif start_ray_local:
        # In this case, we launch a scheduler, a new object store, and some
        # workers, and we connect to them. We do not launch any processes that
        # are already registered in address_info.
        # Use the address 127.0.0.1 in local mode.
        node_ip_address = ("127.0.0.1" if node_ip_address is None
                           else node_ip_address)
        # Use 1 local scheduler if num_local_schedulers is not provided. If
        # existing local schedulers are provided, use that count as
        # num_local_schedulers.
        local_schedulers = address_info.get("local_scheduler_socket_names", [])
        if num_local_schedulers is None:
            if len(local_schedulers) > 0:
                num_local_schedulers = len(local_schedulers)
            else:
                num_local_schedulers = 1
        # Use 1 additional redis shard if num_redis_shards is not provided.
        num_redis_shards = 1 if num_redis_shards is None else num_redis_shards
        # Start the scheduler, object store, and some workers. These will be
        # killed by the call to cleanup(), which happens when the Python script
        # exits.
        address_info = services.start_ray_head(
            address_info=address_info,
            node_ip_address=node_ip_address,
            num_workers=num_workers,
            num_local_schedulers=num_local_schedulers,
            redirect_output=redirect_output,
            start_workers_from_local_scheduler=(
                start_workers_from_local_scheduler),
            num_cpus=num_cpus,
            num_gpus=num_gpus,
            num_redis_shards=num_redis_shards)
    else:
        if redis_address is None:
            raise Exception("When connecting to an existing cluster, "
                            "redis_address must be provided.")
        if num_workers is not None:
            raise Exception("When connecting to an existing cluster, "
                            "num_workers must not be provided.")
        if num_local_schedulers is not None:
            raise Exception("When connecting to an existing cluster, "
                            "num_local_schedulers must not be provided.")
        if num_cpus is not None or num_gpus is not None:
            raise Exception("When connecting to an existing cluster, num_cpus "
                            "and num_gpus must not be provided.")
        if num_redis_shards is not None:
            raise Exception("When connecting to an existing cluster, "
                            "num_redis_shards must not be provided.")
        # Get the node IP address if one is not provided.
        if node_ip_address is None:
            node_ip_address = services.get_node_ip_address(redis_address)
        # Get the address info of the processes to connect to from Redis.
        address_info = get_address_info_from_redis(redis_address,
                                                   node_ip_address)

    # Connect this driver to Redis, the object store, and the local scheduler.
    # Choose the first object store and local scheduler if there are multiple.
    # The corresponding call to disconnect will happen in the call to cleanup()
    # when the Python script exits.
    if driver_mode == PYTHON_MODE:
        driver_address_info = {}
    else:
        driver_address_info = {
            "node_ip_address": node_ip_address,
            "redis_address": address_info["redis_address"],
            "store_socket_name": (
                address_info["object_store_addresses"][0].name),
            "manager_socket_name": (
                address_info["object_store_addresses"][0].manager_name),
            "local_scheduler_socket_name": (
                address_info["local_scheduler_socket_names"][0])}
    connect(driver_address_info, object_id_seed=object_id_seed,
            mode=driver_mode, worker=global_worker, actor_id=NIL_ACTOR_ID)
    return address_info