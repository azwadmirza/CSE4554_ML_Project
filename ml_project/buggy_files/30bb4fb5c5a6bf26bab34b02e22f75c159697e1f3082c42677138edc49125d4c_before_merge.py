def start_ray_processes(address_info=None,
                        node_ip_address="127.0.0.1",
                        redis_port=None,
                        num_workers=None,
                        num_local_schedulers=1,
                        num_redis_shards=1,
                        worker_path=None,
                        cleanup=True,
                        redirect_output=False,
                        include_global_scheduler=False,
                        include_log_monitor=False,
                        include_webui=False,
                        start_workers_from_local_scheduler=True,
                        num_cpus=None,
                        num_gpus=None):
    """Helper method to start Ray processes.

    Args:
        address_info (dict): A dictionary with address information for
            processes that have already been started. If provided, address_info
            will be modified to include processes that are newly started.
        node_ip_address (str): The IP address of this node.
        redis_port (int): The port that the primary Redis shard should listen
            to. If None, then a random port will be chosen. If the key
            "redis_address" is in address_info, then this argument will be
            ignored.
        num_workers (int): The number of workers to start.
        num_local_schedulers (int): The total number of local schedulers
            required. This is also the total number of object stores required.
            This method will start new instances of local schedulers and object
            stores until there are num_local_schedulers existing instances of
            each, including ones already registered with the given
            address_info.
        num_redis_shards: The number of Redis shards to start in addition to
            the primary Redis shard.
        worker_path (str): The path of the source code that will be run by the
            worker.
        cleanup (bool): If cleanup is true, then the processes started here
            will be killed by services.cleanup() when the Python process that
            called this method exits.
        redirect_output (bool): True if stdout and stderr should be redirected
            to a file.
        include_global_scheduler (bool): If include_global_scheduler is True,
            then start a global scheduler process.
        include_log_monitor (bool): If True, then start a log monitor to
            monitor the log files for all processes on this node and push their
            contents to Redis.
        include_webui (bool): If True, then attempt to start the web UI. Note
            that this is only possible with Python 3.
        start_workers_from_local_scheduler (bool): If this flag is True, then
            start the initial workers from the local scheduler. Else, start
            them from Python.
        num_cpus: A list of length num_local_schedulers containing the number
            of CPUs each local scheduler should be configured with.
        num_gpus: A list of length num_local_schedulers containing the number
            of GPUs each local scheduler should be configured with.

    Returns:
        A dictionary of the address information for the processes that were
            started.
    """
    if not isinstance(num_cpus, list):
        num_cpus = num_local_schedulers * [num_cpus]
    if not isinstance(num_gpus, list):
        num_gpus = num_local_schedulers * [num_gpus]
    assert len(num_cpus) == num_local_schedulers
    assert len(num_gpus) == num_local_schedulers

    if num_workers is not None:
        workers_per_local_scheduler = num_local_schedulers * [num_workers]
    else:
        workers_per_local_scheduler = []
        for cpus in num_cpus:
            workers_per_local_scheduler.append(cpus if cpus is not None
                                               else psutil.cpu_count())

    if address_info is None:
        address_info = {}
    address_info["node_ip_address"] = node_ip_address

    if worker_path is None:
        worker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "workers/default_worker.py")

    # Start Redis if there isn't already an instance running. TODO(rkn): We are
    # suppressing the output of Redis because on Linux it prints a bunch of
    # warning messages when it starts up. Instead of suppressing the output, we
    # should address the warnings.
    redis_address = address_info.get("redis_address")
    redis_shards = address_info.get("redis_shards", [])
    if redis_address is None:
        redis_address, redis_shards = start_redis(
            node_ip_address, port=redis_port,
            num_redis_shards=num_redis_shards,
            redirect_output=redirect_output, cleanup=cleanup)
        address_info["redis_address"] = redis_address
        time.sleep(0.1)

        # Start monitoring the processes.
        monitor_stdout_file, monitor_stderr_file = new_log_files(
            "monitor", redirect_output)
        start_monitor(redis_address,
                      node_ip_address,
                      stdout_file=monitor_stdout_file,
                      stderr_file=monitor_stderr_file)

    if redis_shards == []:
        # Get redis shards from primary redis instance.
        redis_ip_address, redis_port = redis_address.split(":")
        redis_client = redis.StrictRedis(host=redis_ip_address,
                                         port=redis_port)
        redis_shards = redis_client.lrange("RedisShards", start=0, end=-1)
        redis_shards = [shard.decode("ascii") for shard in redis_shards]
        address_info["redis_shards"] = redis_shards

    # Start the log monitor, if necessary.
    if include_log_monitor:
        log_monitor_stdout_file, log_monitor_stderr_file = new_log_files(
            "log_monitor", redirect_output=True)
        start_log_monitor(redis_address,
                          node_ip_address,
                          stdout_file=log_monitor_stdout_file,
                          stderr_file=log_monitor_stderr_file,
                          cleanup=cleanup)

    # Start the global scheduler, if necessary.
    if include_global_scheduler:
        global_scheduler_stdout_file, global_scheduler_stderr_file = (
            new_log_files("global_scheduler", redirect_output))
        start_global_scheduler(redis_address,
                               node_ip_address,
                               stdout_file=global_scheduler_stdout_file,
                               stderr_file=global_scheduler_stderr_file,
                               cleanup=cleanup)

    # Initialize with existing services.
    if "object_store_addresses" not in address_info:
        address_info["object_store_addresses"] = []
    object_store_addresses = address_info["object_store_addresses"]
    if "local_scheduler_socket_names" not in address_info:
        address_info["local_scheduler_socket_names"] = []
    local_scheduler_socket_names = address_info["local_scheduler_socket_names"]

    # Get the ports to use for the object managers if any are provided.
    object_manager_ports = (address_info["object_manager_ports"]
                            if "object_manager_ports" in address_info
                            else None)
    if not isinstance(object_manager_ports, list):
        object_manager_ports = num_local_schedulers * [object_manager_ports]
    assert len(object_manager_ports) == num_local_schedulers

    # Start any object stores that do not yet exist.
    for i in range(num_local_schedulers - len(object_store_addresses)):
        # Start Plasma.
        plasma_store_stdout_file, plasma_store_stderr_file = new_log_files(
            "plasma_store_{}".format(i), redirect_output)
        plasma_manager_stdout_file, plasma_manager_stderr_file = new_log_files(
            "plasma_manager_{}".format(i), redirect_output)
        object_store_address = start_objstore(
            node_ip_address,
            redis_address,
            object_manager_port=object_manager_ports[i],
            store_stdout_file=plasma_store_stdout_file,
            store_stderr_file=plasma_store_stderr_file,
            manager_stdout_file=plasma_manager_stdout_file,
            manager_stderr_file=plasma_manager_stderr_file,
            cleanup=cleanup)
        object_store_addresses.append(object_store_address)
        time.sleep(0.1)

    # Start any local schedulers that do not yet exist.
    for i in range(len(local_scheduler_socket_names), num_local_schedulers):
        # Connect the local scheduler to the object store at the same index.
        object_store_address = object_store_addresses[i]
        plasma_address = "{}:{}".format(node_ip_address,
                                        object_store_address.manager_port)
        # Determine how many workers this local scheduler should start.
        if start_workers_from_local_scheduler:
            num_local_scheduler_workers = workers_per_local_scheduler[i]
            workers_per_local_scheduler[i] = 0
        else:
            # If we're starting the workers from Python, the local scheduler
            # should not start any workers.
            num_local_scheduler_workers = 0
        # Start the local scheduler.
        local_scheduler_stdout_file, local_scheduler_stderr_file = (
            new_log_files("local_scheduler_{}".format(i), redirect_output))
        local_scheduler_name = start_local_scheduler(
            redis_address,
            node_ip_address,
            object_store_address.name,
            object_store_address.manager_name,
            worker_path,
            plasma_address=plasma_address,
            stdout_file=local_scheduler_stdout_file,
            stderr_file=local_scheduler_stderr_file,
            cleanup=cleanup,
            num_cpus=num_cpus[i],
            num_gpus=num_gpus[i],
            num_workers=num_local_scheduler_workers)
        local_scheduler_socket_names.append(local_scheduler_name)
        time.sleep(0.1)

    # Make sure that we have exactly num_local_schedulers instances of object
    # stores and local schedulers.
    assert len(object_store_addresses) == num_local_schedulers
    assert len(local_scheduler_socket_names) == num_local_schedulers

    # Start any workers that the local scheduler has not already started.
    for i, num_local_scheduler_workers in enumerate(
            workers_per_local_scheduler):
        object_store_address = object_store_addresses[i]
        local_scheduler_name = local_scheduler_socket_names[i]
        for j in range(num_local_scheduler_workers):
            worker_stdout_file, worker_stderr_file = new_log_files(
                "worker_{}_{}".format(i, j), redirect_output)
            start_worker(node_ip_address,
                         object_store_address.name,
                         object_store_address.manager_name,
                         local_scheduler_name,
                         redis_address,
                         worker_path,
                         stdout_file=worker_stdout_file,
                         stderr_file=worker_stderr_file,
                         cleanup=cleanup)
            workers_per_local_scheduler[i] -= 1

    # Make sure that we've started all the workers.
    assert(sum(workers_per_local_scheduler) == 0)

    # Try to start the web UI.
    if include_webui:
        ui_stdout_file, ui_stderr_file = new_log_files(
            "webui", redirect_output=True)
        start_ui(redis_address, stdout_file=ui_stdout_file,
                 stderr_file=ui_stderr_file, cleanup=cleanup)

    # Return the addresses of the relevant processes.
    return address_info