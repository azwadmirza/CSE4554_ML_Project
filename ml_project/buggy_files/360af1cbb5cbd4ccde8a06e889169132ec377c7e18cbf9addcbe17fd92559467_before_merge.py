def start_raylet(redis_address,
                 node_ip_address,
                 node_manager_port,
                 raylet_name,
                 plasma_store_name,
                 worker_path,
                 temp_dir,
                 session_dir,
                 log_dir,
                 resource_spec,
                 plasma_directory,
                 object_store_memory,
                 min_worker_port=None,
                 max_worker_port=None,
                 worker_port_list=None,
                 object_manager_port=None,
                 redis_password=None,
                 metrics_agent_port=None,
                 metrics_export_port=None,
                 use_valgrind=False,
                 use_profiler=False,
                 stdout_file=None,
                 stderr_file=None,
                 config=None,
                 java_worker_options=None,
                 load_code_from_local=False,
                 huge_pages=False,
                 fate_share=None,
                 socket_to_use=None,
                 head_node=False,
                 start_initial_python_workers_for_first_job=False,
                 code_search_path=None):
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
        log_dir (str): The path of the dir where log files are created.
        resource_spec (ResourceSpec): Resources for this raylet.
        object_manager_port: The port to use for the object manager. If this is
            None, then the object manager will choose its own port.
        min_worker_port (int): The lowest port number that workers will bind
            on. If not set, random ports will be chosen.
        max_worker_port (int): The highest port number that workers will bind
            on. If set, min_worker_port must also be set.
        redis_password: The password to use when connecting to Redis.
        metrics_agent_port(int): The port where metrics agent is bound to.
        metrics_export_port(int): The port at which metrics are exposed to.
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
        java_worker_options (list): The command options for Java worker.
        code_search_path (list): Code search path for worker. code_search_path
            is added to worker command in non-multi-tenancy mode and job_config
            in multi-tenancy mode.
    Returns:
        ProcessInfo for the process that was started.
    """
    # The caller must provide a node manager port so that we can correctly
    # populate the command to start a worker.
    assert node_manager_port is not None and node_manager_port != 0
    config_str = serialize_config(config)

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

    has_java_command = False
    if shutil.which("java") is not None:
        has_java_command = True

    ray_java_installed = False
    try:
        jars_dir = get_ray_jars_dir()
        if os.path.exists(jars_dir):
            ray_java_installed = True
    except Exception:
        pass

    include_java = has_java_command and ray_java_installed
    if include_java is True:
        java_worker_command = build_java_worker_command(
            json.loads(java_worker_options) if java_worker_options else [],
            redis_address,
            node_manager_port,
            plasma_store_name,
            raylet_name,
            redis_password,
            session_dir,
            code_search_path,
        )
    else:
        java_worker_command = []

    if os.path.exists(DEFAULT_WORKER_EXECUTABLE):
        cpp_worker_command = build_cpp_worker_command(
            "",
            redis_address,
            node_manager_port,
            plasma_store_name,
            raylet_name,
            redis_password,
            session_dir,
        )
    else:
        cpp_worker_command = []

    # Create the command that the Raylet will use to start workers.
    start_worker_command = [
        sys.executable, worker_path, f"--node-ip-address={node_ip_address}",
        f"--node-manager-port={node_manager_port}",
        f"--object-store-name={plasma_store_name}",
        f"--raylet-name={raylet_name}", f"--redis-address={redis_address}",
        f"--config-list={config_str}", f"--temp-dir={temp_dir}",
        f"--metrics-agent-port={metrics_agent_port}"
    ]
    if code_search_path:
        start_worker_command.append(f"--code-search-path={code_search_path}")
    if redis_password:
        start_worker_command += [f"--redis-password={redis_password}"]

    # If the object manager port is None, then use 0 to cause the object
    # manager to choose its own port.
    if object_manager_port is None:
        object_manager_port = 0

    if min_worker_port is None:
        min_worker_port = 0

    if max_worker_port is None:
        max_worker_port = 0

    if code_search_path is not None and len(code_search_path) > 0:
        load_code_from_local = True

    if load_code_from_local:
        start_worker_command += ["--load-code-from-local"]

    # Create agent command
    agent_command = [
        sys.executable,
        "-u",
        os.path.join(RAY_PATH, "new_dashboard/agent.py"),
        f"--redis-address={redis_address}",
        f"--metrics-export-port={metrics_export_port}",
        f"--dashboard-agent-port={metrics_agent_port}",
        f"--node-manager-port={node_manager_port}",
        f"--object-store-name={plasma_store_name}",
        f"--raylet-name={raylet_name}",
        f"--temp-dir={temp_dir}",
        f"--log-dir={log_dir}",
    ]

    if redis_password is not None and len(redis_password) != 0:
        agent_command.append("--redis-password={}".format(redis_password))

    command = [
        RAYLET_EXECUTABLE,
        f"--raylet_socket_name={raylet_name}",
        f"--store_socket_name={plasma_store_name}",
        f"--object_manager_port={object_manager_port}",
        f"--min_worker_port={min_worker_port}",
        f"--max_worker_port={max_worker_port}",
        f"--node_manager_port={node_manager_port}",
        f"--node_ip_address={node_ip_address}",
        f"--redis_address={gcs_ip_address}",
        f"--redis_port={gcs_port}",
        f"--num_initial_workers={num_initial_workers}",
        f"--maximum_startup_concurrency={maximum_startup_concurrency}",
        f"--static_resource_list={resource_argument}",
        f"--config_list={config_str}",
        f"--python_worker_command={subprocess.list2cmdline(start_worker_command)}",  # noqa
        f"--java_worker_command={subprocess.list2cmdline(java_worker_command)}",  # noqa
        f"--cpp_worker_command={subprocess.list2cmdline(cpp_worker_command)}",  # noqa
        f"--redis_password={redis_password or ''}",
        f"--temp_dir={temp_dir}",
        f"--session_dir={session_dir}",
        f"--metrics-agent-port={metrics_agent_port}",
        f"--metrics_export_port={metrics_export_port}",
    ]
    if worker_port_list is not None:
        command.append(f"--worker_port_list={worker_port_list}")
    if start_initial_python_workers_for_first_job:
        command.append("--num_initial_python_workers_for_first_job={}".format(
            resource_spec.num_cpus))
    command.append("--agent_command={}".format(
        subprocess.list2cmdline(agent_command)))
    if config.get("plasma_store_as_thread"):
        # command related to the plasma store
        command += [
            f"--object_store_memory={object_store_memory}",
            f"--plasma_directory={plasma_directory}",
        ]
        if huge_pages:
            command.append("--huge_pages")
    if socket_to_use:
        socket_to_use.close()
    if head_node:
        command.append("--head_node")
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