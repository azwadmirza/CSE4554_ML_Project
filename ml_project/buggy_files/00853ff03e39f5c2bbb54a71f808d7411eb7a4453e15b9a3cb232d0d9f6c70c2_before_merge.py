def start(node_ip_address, redis_address, address, redis_port, port,
          num_redis_shards, redis_max_clients, redis_password,
          redis_shard_ports, object_manager_port, node_manager_port,
          gcs_server_port, min_worker_port, max_worker_port, memory,
          object_store_memory, redis_max_memory, num_cpus, num_gpus, resources,
          head, include_webui, webui_host, include_dashboard, dashboard_host,
          dashboard_port, block, plasma_directory, huge_pages,
          autoscaling_config, no_redirect_worker_output, no_redirect_output,
          plasma_store_socket_name, raylet_socket_name, temp_dir,
          java_worker_options, code_search_path, load_code_from_local,
          system_config, lru_evict, enable_object_reconstruction,
          metrics_export_port, log_style, log_color, verbose):
    """Start Ray processes manually on the local machine."""
    cli_logger.log_style = log_style
    cli_logger.color_mode = log_color
    cli_logger.verbosity = verbose
    cli_logger.detect_colors()

    if gcs_server_port and not head:
        raise ValueError(
            "gcs_server_port can be only assigned when you specify --head.")

    if redis_address is not None:
        cli_logger.abort("{} is deprecated. Use {} instead.",
                         cf.bold("--redis-address"), cf.bold("--address"))

        raise DeprecationWarning("The --redis-address argument is "
                                 "deprecated. Please use --address instead.")
    if redis_port is not None:
        cli_logger.warning("{} is being deprecated. Use {} instead.",
                           cf.bold("--redis-port"), cf.bold("--port"))
        cli_logger.old_warning(
            logger, "The --redis-port argument will be deprecated soon. "
            "Please use --port instead.")
        if port is not None and port != redis_port:
            cli_logger.abort(
                "Incompatible values for {} and {}. Use only {} instead.",
                cf.bold("--port"), cf.bold("--redis-port"), cf.bold("--port"))

            raise ValueError("Cannot specify both --port and --redis-port "
                             "as port is a rename of deprecated redis-port")
    if include_webui is not None:
        cli_logger.warning("{} is being deprecated. Use {} instead.",
                           cf.bold("--include-webui"),
                           cf.bold("--include-dashboard"))
        cli_logger.old_warning(
            logger, "The --include-webui argument will be deprecated soon"
            "Please use --include-dashboard instead.")
        if include_dashboard is not None:
            include_dashboard = include_webui

    dashboard_host_default = "localhost"
    if webui_host != dashboard_host_default:
        cli_logger.warning("{} is being deprecated. Use {} instead.",
                           cf.bold("--webui-host"),
                           cf.bold("--dashboard-host"))
        cli_logger.old_warning(
            logger, "The --webui-host argument will be deprecated"
            " soon. Please use --dashboard-host instead.")
        if webui_host != dashboard_host and dashboard_host != "localhost":
            cli_logger.abort(
                "Incompatible values for {} and {}. Use only {} instead.",
                cf.bold("--dashboard-host"), cf.bold("--webui-host"),
                cf.bold("--dashboard-host"))

            raise ValueError(
                "Cannot specify both --webui-host and --dashboard-host,"
                " please specify only the latter")
        else:
            dashboard_host = webui_host

    # Convert hostnames to numerical IP address.
    if node_ip_address is not None:
        node_ip_address = services.address_to_ip(node_ip_address)

    if address is not None:
        (redis_address, redis_address_ip,
         redis_address_port) = services.validate_redis_address(address)

    try:
        resources = json.loads(resources)
    except Exception:
        cli_logger.error("`{}` is not a valid JSON string.",
                         cf.bold("--resources"))
        cli_logger.abort(
            "Valid values look like this: `{}`",
            cf.bold("--resources='\"CustomResource3\": 1, "
                    "\"CustomResource2\": 2}'"))

        raise Exception("Unable to parse the --resources argument using "
                        "json.loads. Try using a format like\n\n"
                        "    --resources='{\"CustomResource1\": 3, "
                        "\"CustomReseource2\": 2}'")

    redirect_worker_output = None if not no_redirect_worker_output else True
    redirect_output = None if not no_redirect_output else True
    ray_params = ray.parameter.RayParams(
        node_ip_address=node_ip_address,
        min_worker_port=min_worker_port,
        max_worker_port=max_worker_port,
        object_manager_port=object_manager_port,
        node_manager_port=node_manager_port,
        gcs_server_port=gcs_server_port,
        memory=memory,
        object_store_memory=object_store_memory,
        redis_password=redis_password,
        redirect_worker_output=redirect_worker_output,
        redirect_output=redirect_output,
        num_cpus=num_cpus,
        num_gpus=num_gpus,
        resources=resources,
        plasma_directory=plasma_directory,
        huge_pages=huge_pages,
        plasma_store_socket_name=plasma_store_socket_name,
        raylet_socket_name=raylet_socket_name,
        temp_dir=temp_dir,
        include_dashboard=include_dashboard,
        dashboard_host=dashboard_host,
        dashboard_port=dashboard_port,
        java_worker_options=java_worker_options,
        load_code_from_local=load_code_from_local,
        code_search_path=code_search_path,
        _system_config=system_config,
        lru_evict=lru_evict,
        enable_object_reconstruction=enable_object_reconstruction,
        metrics_export_port=metrics_export_port)
    if head:
        # Start Ray on the head node.
        if redis_shard_ports is not None:
            redis_shard_ports = redis_shard_ports.split(",")
            # Infer the number of Redis shards from the ports if the number is
            # not provided.
            if num_redis_shards is None:
                num_redis_shards = len(redis_shard_ports)
            # Check that the arguments match.
            if len(redis_shard_ports) != num_redis_shards:
                cli_logger.error(
                    "`{}` must be a comma-separated list of ports, "
                    "with length equal to `{}` (which defaults to {})",
                    cf.bold("--redis-shard-ports"),
                    cf.bold("--num-redis-shards"), cf.bold("1"))
                cli_logger.abort(
                    "Example: `{}`",
                    cf.bold("--num-redis-shards 3 "
                            "--redis_shard_ports 6380,6381,6382"))

                raise Exception("If --redis-shard-ports is provided, it must "
                                "have the form '6380,6381,6382', and the "
                                "number of ports provided must equal "
                                "--num-redis-shards (which is 1 if not "
                                "provided)")

        if redis_address is not None:
            cli_logger.abort(
                "`{}` starts a new Redis server, `{}` should not be set.",
                cf.bold("--head"), cf.bold("--address"))

            raise Exception("If --head is passed in, a Redis server will be "
                            "started, so a Redis address should not be "
                            "provided.")

        # Get the node IP address if one is not provided.
        ray_params.update_if_absent(
            node_ip_address=services.get_node_ip_address())
        cli_logger.labeled_value("Local node IP", ray_params.node_ip_address)
        cli_logger.old_info(logger, "Using IP address {} for this node.",
                            ray_params.node_ip_address)
        ray_params.update_if_absent(
            redis_port=port or redis_port,
            redis_shard_ports=redis_shard_ports,
            redis_max_memory=redis_max_memory,
            num_redis_shards=num_redis_shards,
            redis_max_clients=redis_max_clients,
            autoscaling_config=autoscaling_config,
        )

        node = ray.node.Node(
            ray_params, head=True, shutdown_at_exit=block, spawn_reaper=block)
        redis_address = node.redis_address

        # this is a noop if new-style is not set, so the old logger calls
        # are still in place
        cli_logger.newline()
        startup_msg = "Ray runtime started."
        cli_logger.success("-" * len(startup_msg))
        cli_logger.success(startup_msg)
        cli_logger.success("-" * len(startup_msg))
        cli_logger.newline()
        with cli_logger.group("Next steps"):
            cli_logger.print(
                "To connect to this Ray runtime from another node, run")
            cli_logger.print(
                cf.bold("  ray start --address='{}'{}"), redis_address,
                f" --redis-password='{redis_password}'"
                if redis_password else "")
            cli_logger.newline()
            cli_logger.print("Alternatively, use the following Python code:")
            with cli_logger.indented():
                with cf.with_style("monokai") as c:
                    cli_logger.print("{} ray", c.magenta("import"))
                    cli_logger.print(
                        "ray{}init(address{}{}{})", c.magenta("."),
                        c.magenta("="), c.yellow("'auto'"),
                        ", redis_password{}{}".format(
                            c.magenta("="),
                            c.yellow("'" + redis_password + "'"))
                        if redis_password else "")
            cli_logger.newline()
            cli_logger.print(
                cf.underlined("If connection fails, check your "
                              "firewall settings other "
                              "network configuration."))
            cli_logger.newline()
            cli_logger.print("To terminate the Ray runtime, run")
            cli_logger.print(cf.bold("  ray stop"))

        cli_logger.old_info(
            logger,
            "\nStarted Ray on this node. You can add additional nodes to "
            "the cluster by calling\n\n"
            "    ray start --address='{}'{}\n\n"
            "from the node you wish to add. You can connect a driver to the "
            "cluster from Python by running\n\n"
            "    import ray\n"
            "    ray.init(address='auto'{})\n\n"
            "If you have trouble connecting from a different machine, check "
            "that your firewall is configured properly. If you wish to "
            "terminate the processes that have been started, run\n\n"
            "    ray stop".format(
                redis_address, " --redis-password='" + redis_password + "'"
                if redis_password else "",
                ", redis_password='" + redis_password + "'"
                if redis_password else ""))
    else:
        # Start Ray on a non-head node.
        if not (redis_port is None and port is None):
            cli_logger.abort("`{}/{}` should not be specified without `{}`.",
                             cf.bold("--port"), cf.bold("--redis-port"),
                             cf.bold("--head"))

            raise Exception(
                "If --head is not passed in, --port and --redis-port are not "
                "allowed.")
        if redis_shard_ports is not None:
            cli_logger.abort("`{}` should not be specified without `{}`.",
                             cf.bold("--redis-shard-ports"), cf.bold("--head"))

            raise Exception("If --head is not passed in, --redis-shard-ports "
                            "is not allowed.")
        if redis_address is None:
            cli_logger.abort("`{}` is required unless starting with `{}`.",
                             cf.bold("--address"), cf.bold("--head"))

            raise Exception("If --head is not passed in, --address must "
                            "be provided.")
        if num_redis_shards is not None:
            cli_logger.abort("`{}` should not be specified without `{}`.",
                             cf.bold("--num-redis-shards"), cf.bold("--head"))

            raise Exception("If --head is not passed in, --num-redis-shards "
                            "must not be provided.")
        if redis_max_clients is not None:
            cli_logger.abort("`{}` should not be specified without `{}`.",
                             cf.bold("--redis-max-clients"), cf.bold("--head"))

            raise Exception("If --head is not passed in, --redis-max-clients "
                            "must not be provided.")
        if include_webui:
            cli_logger.abort("`{}` should not be specified without `{}`.",
                             cf.bold("--include-web-ui"), cf.bold("--head"))

            raise Exception("If --head is not passed in, the --include-webui"
                            "flag is not relevant.")
        if include_dashboard:
            cli_logger.abort("`{}` should not be specified without `{}`.",
                             cf.bold("--include-dashboard"), cf.bold("--head"))

            raise ValueError(
                "If --head is not passed in, the --include-dashboard"
                "flag is not relevant.")

        # Wait for the Redis server to be started. And throw an exception if we
        # can't connect to it.
        services.wait_for_redis_to_start(
            redis_address_ip, redis_address_port, password=redis_password)

        # Create a Redis client.
        redis_client = services.create_redis_client(
            redis_address, password=redis_password)

        # Check that the version information on this node matches the version
        # information that the cluster was started with.
        services.check_version_info(redis_client)

        # Get the node IP address if one is not provided.
        ray_params.update_if_absent(
            node_ip_address=services.get_node_ip_address(redis_address))

        cli_logger.labeled_value("Local node IP", ray_params.node_ip_address)
        cli_logger.old_info(logger, "Using IP address {} for this node.",
                            ray_params.node_ip_address)

        # Check that there aren't already Redis clients with the same IP
        # address connected with this Redis instance. This raises an exception
        # if the Redis server already has clients on this node.
        check_no_existing_redis_clients(ray_params.node_ip_address,
                                        redis_client)
        ray_params.update(redis_address=redis_address)
        node = ray.node.Node(
            ray_params, head=False, shutdown_at_exit=block, spawn_reaper=block)

        cli_logger.newline()
        startup_msg = "Ray runtime started."
        cli_logger.success("-" * len(startup_msg))
        cli_logger.success(startup_msg)
        cli_logger.success("-" * len(startup_msg))
        cli_logger.newline()
        cli_logger.print("To terminate the Ray runtime, run")
        cli_logger.print(cf.bold("  ray stop"))

        cli_logger.old_info(
            logger, "\nStarted Ray on this node. If you wish to terminate the "
            "processes that have been started, run\n\n"
            "    ray stop")

    if block:
        cli_logger.newline()
        with cli_logger.group(cf.bold("--block")):
            cli_logger.print(
                "This command will now block until terminated by a signal.")
            cli_logger.print(
                "Runing subprocesses are monitored and a message will be "
                "printed if any of them terminate unexpectedly.")

        while True:
            time.sleep(1)
            deceased = node.dead_processes()
            if len(deceased) > 0:
                cli_logger.newline()
                cli_logger.error("Some Ray subprcesses exited unexpectedly:")
                cli_logger.old_error(logger,
                                     "Ray processes died unexpectedly:")

                with cli_logger.indented():
                    for process_type, process in deceased:
                        cli_logger.error(
                            "{}",
                            cf.bold(str(process_type)),
                            _tags={"exit code": str(process.returncode)})
                        cli_logger.old_error(
                            logger, "\t{} died with exit code {}".format(
                                process_type, process.returncode))

                # shutdown_at_exit will handle cleanup.
                cli_logger.newline()
                cli_logger.error("Remaining processes will be killed.")
                cli_logger.old_error(
                    logger, "Killing remaining processes and exiting...")
                sys.exit(1)