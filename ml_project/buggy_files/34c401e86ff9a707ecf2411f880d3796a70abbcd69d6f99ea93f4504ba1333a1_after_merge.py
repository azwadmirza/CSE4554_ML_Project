def main(args):
    from debugpy import adapter
    from debugpy.common import compat, log, sockets
    from debugpy.adapter import ide, servers, sessions

    if args.for_server is not None:
        if os.name == "posix":
            # On POSIX, we need to leave the process group and its session, and then
            # daemonize properly by double-forking (first fork already happened when
            # this process was spawned).
            os.setsid()
            if os.fork() != 0:
                sys.exit(0)

        for stdio in sys.stdin, sys.stdout, sys.stderr:
            if stdio is not None:
                stdio.close()

    if args.log_stderr:
        log.stderr.levels |= set(log.LEVELS)
    if args.log_dir is not None:
        log.log_dir = args.log_dir

    log.to_file(prefix="debugpy.adapter")
    log.describe_environment("debugpy.adapter startup environment:")

    servers.access_token = args.server_access_token
    if args.for_server is None:
        adapter.access_token = compat.force_str(codecs.encode(os.urandom(32), "hex"))

    try:
        server_host, server_port = servers.serve()
    except Exception as exc:
        if args.for_server is None:
            raise
        endpoints = {"error": "Can't listen for server connections: " + str(exc)}
    else:
        endpoints = {"server": {"host": server_host, "port": server_port}}
        try:
            ide_host, ide_port = ide.serve(args.host, args.port)
        except Exception as exc:
            if args.for_server is None:
                raise
            endpoints = {
                "error": "Can't listen for IDE connections: " + str(exc)
            }
        else:
            endpoints["ide"] = {"host": ide_host, "port": ide_port}

    if args.for_server is not None:
        log.info(
            "Sending endpoints info to debug server at localhost:{0}:\n{1!j}",
            args.for_server,
            endpoints,
        )

        try:
            sock = sockets.create_client()
            try:
                sock.settimeout(None)
                sock.connect(("127.0.0.1", args.for_server))
                sock_io = sock.makefile("wb", 0)
                try:
                    sock_io.write(json.dumps(endpoints).encode("utf-8"))
                finally:
                    sock_io.close()
            finally:
                sockets.close_socket(sock)
        except Exception:
            raise log.exception("Error sending endpoints info to debug server:")

        if "error" in endpoints:
            log.error("Couldn't set up endpoints; exiting.")
            sys.exit(1)

    listener_file = os.getenv("DEBUGPY_ADAPTER_ENDPOINTS")
    if listener_file is not None:
        log.info(
            "Writing endpoints info to {0!r}:\n{1!j}", listener_file, endpoints
        )

        def delete_listener_file():
            log.info("Listener ports closed; deleting {0!r}", listener_file)
            try:
                os.remove(listener_file)
            except Exception:
                log.exception("Failed to delete {0!r}", listener_file, level="warning")

        try:
            with open(listener_file, "w") as f:
                atexit.register(delete_listener_file)
                print(json.dumps(endpoints), file=f)
        except Exception:
            raise log.exception("Error writing endpoints info to file:")

    if args.port is None:
        ide.IDE("stdio")

    # These must be registered after the one above, to ensure that the listener sockets
    # are closed before the endpoint info file is deleted - this way, another process
    # can wait for the file to go away as a signal that the ports are no longer in use.
    atexit.register(servers.stop_serving)
    atexit.register(ide.stop_serving)

    servers.wait_until_disconnected()
    log.info("All debug servers disconnected; waiting for remaining sessions...")

    sessions.wait_until_ended()
    log.info("All debug sessions have ended; exiting.")