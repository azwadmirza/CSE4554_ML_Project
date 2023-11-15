def start_ray_head(address_info=None,
                   node_ip_address="127.0.0.1",
                   redis_port=None,
                   num_workers=0,
                   num_local_schedulers=1,
                   worker_path=None,
                   cleanup=True,
                   redirect_output=False,
                   start_workers_from_local_scheduler=True,
                   num_cpus=None,
                   num_gpus=None,
                   num_redis_shards=None):
    """Start Ray in local mode.

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
            stores until there are at least num_local_schedulers existing
            instances of each, including ones already registered with the given
            address_info.
        worker_path (str): The path of the source code that will be run by the
            worker.
        cleanup (bool): If cleanup is true, then the processes started here
            will be killed by services.cleanup() when the Python process that
            called this method exits.
        redirect_output (bool): True if stdout and stderr should be redirected
            to a file.
        start_workers_from_local_scheduler (bool): If this flag is True, then
            start the initial workers from the local scheduler. Else, start
            them from Python.
        num_cpus (int): number of cpus to configure the local scheduler with.
        num_gpus (int): number of gpus to configure the local scheduler with.
        num_redis_shards: The number of Redis shards to start in addition to
            the primary Redis shard.

    Returns:
        A dictionary of the address information for the processes that were
            started.
    """
    num_redis_shards = 1 if num_redis_shards is None else num_redis_shards
    return start_ray_processes(
        address_info=address_info,
        node_ip_address=node_ip_address,
        redis_port=redis_port,
        num_workers=num_workers,
        num_local_schedulers=num_local_schedulers,
        worker_path=worker_path,
        cleanup=cleanup,
        redirect_output=redirect_output,
        include_global_scheduler=True,
        include_log_monitor=True,
        include_webui=True,
        start_workers_from_local_scheduler=start_workers_from_local_scheduler,
        num_cpus=num_cpus,
        num_gpus=num_gpus,
        num_redis_shards=num_redis_shards)