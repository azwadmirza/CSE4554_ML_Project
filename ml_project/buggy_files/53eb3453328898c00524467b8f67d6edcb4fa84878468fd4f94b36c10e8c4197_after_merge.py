def top(opts):
    if not ENABLED:
        raise Exception('Could not import tracemalloc')
    lines = opts.lines
    seconds = opts.seconds
    force_start = opts.force_start
    if opts.socket is None:
        socket = ipc.find_sockfile()
    else:
        socket = opts.socket
    client = ipc.Client(socket)
    client = command_interface.IPCCommandInterface(client)
    client = command_client.InteractiveCommandClient(client)

    try:
        if not opts.raw:
            curses.wrapper(get_stats, client, limit=lines, seconds=seconds,
                           force_start=force_start)
        else:
            raw_stats(client, limit=lines, force_start=force_start)
    except TraceNotStarted:
        print("tracemalloc not started on qtile, start by setting "
              "PYTHONTRACEMALLOC=1 before starting qtile")
        print("or force start tracemalloc now, but you'll lose early traces")
        exit(1)
    except TraceCantStart:
        print("Can't start tracemalloc on qtile, check the logs")
    except KeyboardInterrupt:
        exit(-1)
    except curses.error:
        print("Terminal too small for curses interface.")
        raw_stats(client, limit=lines, force_start=force_start)