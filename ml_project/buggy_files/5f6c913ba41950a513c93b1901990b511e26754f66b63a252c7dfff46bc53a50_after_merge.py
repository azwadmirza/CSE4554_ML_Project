def start_dashboard(require_dashboard,
                    host,
                    redis_address,
                    temp_dir,
                    logdir,
                    port=ray_constants.DEFAULT_DASHBOARD_PORT,
                    stdout_file=None,
                    stderr_file=None,
                    redis_password=None,
                    fate_share=None,
                    max_bytes=0,
                    backup_count=0):
    """Start a dashboard process.

    Args:
        require_dashboard (bool): If true, this will raise an exception if we
            fail to start the dashboard. Otherwise it will print a warning if
            we fail to start the dashboard.
        host (str): The host to bind the dashboard web server to.
        port (str): The port to bind the dashboard web server to.
            Defaults to 8265.
        redis_address (str): The address of the Redis instance.
        temp_dir (str): The temporary directory used for log files and
            information for this Ray session.
        logdir (str): The log directory used to generate dashboard log.
        stdout_file: A file handle opened for writing to redirect stdout to. If
            no redirection should happen, then this should be None.
        stderr_file: A file handle opened for writing to redirect stderr to. If
            no redirection should happen, then this should be None.
        redis_password (str): The password of the redis server.
        max_bytes (int): Log rotation parameter. Corresponding to
            RotatingFileHandler's maxBytes.
        backup_count (int): Log rotation parameter. Corresponding to
            RotatingFileHandler's backupCount.

    Returns:
        ProcessInfo for the process that was started.
    """
    port_retries = 10
    if port != ray_constants.DEFAULT_DASHBOARD_PORT:
        port_test_socket = socket.socket()
        port_test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            port_test_socket.bind(("127.0.0.1", port))
            port_test_socket.close()
        except socket.error:
            raise ValueError(
                f"The given dashboard port {port} is already in use")
        port_retries = 0

    dashboard_dir = "new_dashboard"
    dashboard_filepath = os.path.join(RAY_PATH, dashboard_dir, "dashboard.py")
    command = [
        sys.executable, "-u", dashboard_filepath, f"--host={host}",
        f"--port={port}", f"--port-retries={port_retries}",
        f"--redis-address={redis_address}", f"--temp-dir={temp_dir}",
        f"--log-dir={logdir}", f"--logging-rotate-bytes={max_bytes}",
        f"--logging-rotate-backup-count={backup_count}"
    ]

    if redis_password:
        command += ["--redis-password", redis_password]

    dashboard_dependencies_present = True
    try:
        import aiohttp  # noqa: F401
        import grpc  # noqa: F401
    except ImportError:
        dashboard_dependencies_present = False
        warning_message = (
            "Failed to start the dashboard. The dashboard requires Python 3 "
            "as well as 'pip install aiohttp grpcio'.")
        if require_dashboard:
            raise ImportError(warning_message)
        else:
            logger.warning(warning_message)
    if dashboard_dependencies_present:
        process_info = start_ray_process(
            command,
            ray_constants.PROCESS_TYPE_DASHBOARD,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
            fate_share=fate_share)

        redis_client = ray._private.services.create_redis_client(
            redis_address, redis_password)

        dashboard_url = None
        dashboard_returncode = None
        for _ in range(20):
            dashboard_url = redis_client.get(ray_constants.REDIS_KEY_DASHBOARD)
            if dashboard_url is not None:
                dashboard_url = dashboard_url.decode("utf-8")
                break
            dashboard_returncode = process_info.process.poll()
            if dashboard_returncode is not None:
                break
            time.sleep(1)
        if dashboard_url is None:
            dashboard_log = os.path.join(logdir, "dashboard.log")
            returncode_str = (f", return code {dashboard_returncode}"
                              if dashboard_returncode is not None else "")
            # Read last n lines of dashboard log. The log file may be large.
            n = 10
            lines = []
            try:
                with open(dashboard_log, "rb") as f:
                    with mmap.mmap(
                            f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        end = mm.size()
                        for _ in range(n):
                            sep = mm.rfind(b"\n", 0, end - 1)
                            if sep == -1:
                                break
                            lines.append(mm[sep + 1:end].decode("utf-8"))
                            end = sep
                lines.append(f" The last {n} lines of {dashboard_log}:")
            except Exception:
                pass
            last_log_str = "\n".join(reversed(lines[-n:]))
            raise Exception("Failed to start the dashboard"
                            f"{returncode_str}.{last_log_str}")

        logger.info("View the Ray dashboard at %s%shttp://%s%s%s",
                    colorama.Style.BRIGHT, colorama.Fore.GREEN, dashboard_url,
                    colorama.Fore.RESET, colorama.Style.NORMAL)

        return dashboard_url, process_info
    else:
        return None, None