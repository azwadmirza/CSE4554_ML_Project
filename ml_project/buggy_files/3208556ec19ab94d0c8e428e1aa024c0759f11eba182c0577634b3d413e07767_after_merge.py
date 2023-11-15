def spawn_debuggee(session, start_request, sudo, args, console, console_title):
    cmdline = ["sudo"] if sudo else []
    cmdline += [sys.executable, os.path.dirname(launcher.__file__)]
    cmdline += args
    env = {}

    arguments = dict(start_request.arguments)
    if not session.no_debug:
        _, arguments["port"] = servers.listener.getsockname()
        arguments["clientAccessToken"] = adapter.access_token

    def on_launcher_connected(sock):
        listener.close()
        stream = messaging.JsonIOStream.from_socket(sock)
        Launcher(session, stream)

    listener = sockets.serve("Launcher", on_launcher_connected, "127.0.0.1", backlog=0)
    try:
        _, launcher_port = listener.getsockname()

        env[str("DEBUGPY_LAUNCHER_PORT")] = str(launcher_port)
        if log.log_dir is not None:
            env[str("DEBUGPY_LOG_DIR")] = compat.filename_str(log.log_dir)
        if log.stderr.levels != {"warning", "error"}:
            env[str("DEBUGPY_LOG_STDERR")] = str(" ".join(log.stderr.levels))

        if console == "internalConsole":
            log.info("{0} spawning launcher: {1!r}", session, cmdline)

            # If we are talking to the IDE over stdio, sys.stdin and sys.stdout are
            # redirected to avoid mangling the DAP message stream. Make sure the
            # launcher also respects that.
            subprocess.Popen(
                cmdline,
                env=dict(list(os.environ.items()) + list(env.items())),
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

        else:
            log.info('{0} spawning launcher via "runInTerminal" request.', session)
            session.ide.capabilities.require("supportsRunInTerminalRequest")
            kinds = {
                "integratedTerminal": "integrated",
                "externalTerminal": "external",
            }
            session.ide.channel.request(
                "runInTerminal",
                {
                    "kind": kinds[console],
                    "title": console_title,
                    "args": cmdline,
                    "env": env,
                },
            )

        if not session.wait_for(lambda: session.launcher, timeout=10):
            raise start_request.cant_handle(
                '{0} timed out waiting for {1} to connect',
                session,
                session.launcher,
            )

        try:
            session.launcher.channel.request(start_request.command, arguments)
        except messaging.MessageHandlingError as exc:
            exc.propagate(start_request)

        if session.no_debug:
            return

        if not session.wait_for(lambda: session.launcher.pid is not None, timeout=10):
            raise start_request.cant_handle(
                '{0} timed out waiting for "process" event from {1}',
                session,
                session.launcher,
            )

        # Wait for the first incoming connection regardless of the PID - it won't
        # necessarily match due to the use of stubs like py.exe or "conda run".
        conn = servers.wait_for_connection(session, lambda conn: True, timeout=10)
        if conn is None:
            raise start_request.cant_handle(
                "{0} timed out waiting for debuggee to spawn", session
            )
        conn.attach_to_session(session)

    finally:
        listener.close()