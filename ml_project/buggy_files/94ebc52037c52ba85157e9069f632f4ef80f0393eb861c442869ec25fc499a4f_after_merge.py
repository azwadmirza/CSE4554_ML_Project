def inject(pid, debugpy_args):
    host, port = listener.getsockname()

    cmdline = [
        sys.executable,
        compat.filename(os.path.dirname(debugpy.__file__)),
        "--client",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if adapter.access_token is not None:
        cmdline += ["--client-access-token", adapter.access_token]
    cmdline += debugpy_args
    cmdline += ["--pid", str(pid)]

    log.info("Spawning attach-to-PID debugger injector: {0!r}", cmdline)
    try:
        injector = subprocess.Popen(
            cmdline,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except Exception as exc:
        log.exception("Failed to inject debug server into process with PID={0}", pid)
        raise messaging.MessageHandlingError(
            fmt(
                "Failed to inject debug server into process with PID={0}: {1}", pid, exc
            )
        )

    # We need to capture the output of the injector - otherwise it can get blocked
    # on a write() syscall when it tries to print something.

    def capture_output():
        while True:
            line = injector.stdout.readline()
            if not line:
                break
            log.info("Injector[PID={0}] output:\n{1}", pid, line.rstrip())
        log.info("Injector[PID={0}] exited.", pid)

    thread = threading.Thread(
        target=capture_output, name=fmt("Injector[PID={0}] output", pid)
    )
    thread.daemon = True
    thread.start()