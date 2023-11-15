def start_raylet(redis_address,
                 node_ip_address,
                 node_manager_port,
                 raylet_name,
                 plasma_store_name,
                 worker_path,
                 temp_dir,
                 session_dir,
                 resource_spec,
                 min_worker_port=None,
                 max_worker_port=None,
                 object_manager_port=None,
                 redis_password=None,
                 use_valgrind=False,
                 use_profiler=False,
                 stdout_file=None,
                 stderr_file=None,
                 config=None,
                 include_java=False,
                 java_worker_options=None,
                 load_code_from_local=False,
                 fate_share=None):
    """Start a raylet, which is a combined local scheduler and object manager.

    Args:
        redis_address (str): The address of the primary Redis server.
        node_ip_address (str): The IP address of this node.
        node_manager_port(int): The port to use for the node manager. This must
            not be 0.
        raylet_name (str): The name of the raylet socket to create.
        plasma_store_name (str): The name of the plasma store socket to connect
             to.
        worker_path (str): The path of the Python file that new worker
            processes will execute.
        temp_dir (str): The path of the temporary directory Ray will use.
        session_dir (str): The path of this session.
        resource_spec (ResourceSpec): Resources for this raylet.
        object_manager_port: The port to use for the object manager. If this is
            None, then the object manager will choose its own port.
        min_worker_port (int): The lowest port number that workers will bind
            on. If not set, random ports will be chosen.
        max_worker_port (int): The highest port number that workers will bind
            on. If set, min_worker_port must also be set.
        redis_password: The password to use when connecting to Redis.
        use_valgrind (bool): True if the raylet should be started inside
            of valgrind. If this is True, use_profiler must be False.
        use_profiler (bool): True if the raylet should be started inside
            a profiler. If this is True, use_valgrind must be False.
        stdout_file: A file handle opened for writing to redirect stdout to. If
            no redirection should happen, then this should be None.
        stderr_file: A file handle opened for writing to redirect stderr to. If
            no redirection should happen, then this should be None.
        config (dict|None): Optional Raylet configuration that will
            override defaults in RayConfig.
        include_java (bool): If True, the raylet backend can also support
            Java worker.
        java_worker_options (list): The command options for Java worker.
    Returns:
        ProcessInfo for the process that was started.
    """
    # The caller must provide a node manager port so that we can correctly
    # populate the command to start a worker.
    assert node_manager_port is not None and node_manager_port != 0
    config = config or {}
    config_str = ",".join(["{},{}".format(*kv) for kv in config.items()])

    if use_valgrind and use_profiler:
        raise ValueError("Cannot use valgrind and profiler at the same time.")

    assert resource_spec.resolved()
    num_initial_workers = resource_spec.num_cpus
    static_resources = resource_spec.to_resource_dict()

    # Limit the number of workers that can be started in parallel by the
    # raylet. However, make sure it is at least 1.
    num_cpus_static = static_resources.get("CPU", 0)
    maximum_startup_concurrency = max(
        1, min(multiprocessing.cpu_count(), num_cpus_static))

    # Format the resource argument in a form like 'CPU,1.0,GPU,0,Custom,3'.
    resource_argument = ",".join(
        ["{},{}".format(*kv) for kv in static_resources.items()])

    gcs_ip_address, gcs_port = redis_address.split(":")

    if include_java is True:
        default_cp = os.pathsep.join(DEFAULT_JAVA_WORKER_CLASSPATH)
        java_worker_command = build_java_worker_command(
            json.loads(java_worker_options)
            if java_worker_options else ["-classpath", default_cp],
            redis_address,
            node_manager_port,
            plasma_store_name,
            raylet_name,
            redis_password,
            session_dir,
        )
    else:
        java_worker_command = []

    # Create the command that the Raylet will use to start workers.
    start_worker_command = [
        sys.executable,
        worker_path,
        "--node-ip-address={}".format(node_ip_address),
        "--node-manager-port={}".format(node_manager_port),
        "--object-store-name={}".format(plasma_store_name),
        "--raylet-name={}".format(raylet_name),
        "--redis-address={}".format(redis_address),
        "--config-list={}".format(config_str),
        "--temp-dir={}".format(temp_dir),
    ]
    if redis_password:
        start_worker_command += ["--redis-password={}".format(redis_password)]

    # If the object manager port is None, then use 0 to cause the object
    # manager to choose its own port.
    if object_manager_port is None:
        object_manager_port = 0

    if min_worker_port is None:
        min_worker_port = 0

    if max_worker_port is None:
        max_worker_port = 0

    if load_code_from_local:
        start_worker_command += ["--load-code-from-local"]

    command = [
        RAYLET_EXECUTABLE,
        "--raylet_socket_name={}".format(raylet_name),
        "--store_socket_name={}".format(plasma_store_name),
        "--object_manager_port={}".format(object_manager_port),
        "--min_worker_port={}".format(min_worker_port),
        "--max_worker_port={}".format(max_worker_port),
        "--node_manager_port={}".format(node_manager_port),
        "--node_ip_address={}".format(node_ip_address),
        "--redis_address={}".format(gcs_ip_address),
        "--redis_port={}".format(gcs_port),
        "--num_initial_workers={}".format(num_initial_workers),
        "--maximum_startup_concurrency={}".format(maximum_startup_concurrency),
        "--static_resource_list={}".format(resource_argument),
        "--config_list={}".format(config_str),
        "--python_worker_command={}".format(
            subprocess.list2cmdline(start_worker_command)),
        "--java_worker_command={}".format(
            subprocess.list2cmdline(java_worker_command)),
        "--redis_password={}".format(redis_password or ""),
        "--temp_dir={}".format(temp_dir),
        "--session_dir={}".format(session_dir),
    ]
    process_info = start_ray_process(
        command,
        ray_constants.PROCESS_TYPE_RAYLET,
        use_valgrind=use_valgrind,
        use_gdb=False,
        use_valgrind_profiler=use_profiler,
        use_perftools_profiler=("RAYLET_PERFTOOLS_PATH" in os.environ),
        stdout_file=stdout_file,
        stderr_file=stderr_file,
        fate_share=fate_share)

    return process_info