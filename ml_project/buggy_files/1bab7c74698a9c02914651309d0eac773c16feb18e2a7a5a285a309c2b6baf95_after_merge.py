def execute(command, env=None, stdout=None, stderr=None, index=None, events=None,
            prefix_output_with_timestamp=False):
    """
    Execute the given command and forward stdout and stderr of the command to the given
    stdout and stderr text streams, or sys.stdout and sys.stderr, respectively, if None given.
    Prefixes each line with index and timestamp if index is not None. The timestamp
    can be disabled with prefix_output_with_timestamp set False.
    The command will be terminated when any of the given events are set.

    :param command: command to execute
    :param env: environment variables to execute command with
    :param stdout: stdout text stream, sys.stdout if None
    :param stderr: stderr text stream, sys.stderr if None
    :param index: index used to prepend text streams
    :param events: events to terminate the command
    :param prefix_output_with_timestamp: prepend text streams with timestamp if True
    :return: command's exit code
    """
    ctx = multiprocessing.get_context('spawn')

    # When this event is set, signal to middleman to terminate its children and exit.
    exit_event = _create_event(ctx)

    # Make a pipe for the subprocess stdout/stderr.
    (stdout_r, stdout_w) = ctx.Pipe()
    (stderr_r, stderr_w) = ctx.Pipe()

    # This Pipe is how we ensure that the executed process is properly terminated (not orphaned) if
    # the parent process is hard killed (-9). If the parent (this process) is killed for any reason,
    # this Pipe will be closed, which can be detected by the middleman. When the middleman sees the
    # closed Pipe, it will issue a SIGTERM to the subprocess executing the command. The assumption
    # here is that users will be inclined to hard kill this process, not the middleman.
    (r, w) = ctx.Pipe()

    middleman = ctx.Process(target=_exec_middleman, args=(command, env, exit_event,
                                                          (stdout_r, stdout_w),
                                                          (stderr_r, stderr_w),
                                                          (r, w)))
    middleman.start()

    # Close unused file descriptors to enforce PIPE behavior.
    r.close()
    stdout_w.close()
    stderr_w.close()

    # Redirect command stdout & stderr to provided streams or sys.stdout/sys.stderr.
    # This is useful for Jupyter Notebook that uses custom sys.stdout/sys.stderr or
    # for redirecting to a file on disk.
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout_fwd = in_thread(target=prefix_connection, args=(stdout_r, stdout, 'stdout', index, prefix_output_with_timestamp))
    stderr_fwd = in_thread(target=prefix_connection, args=(stderr_r, stderr, 'stderr', index, prefix_output_with_timestamp))

    # TODO: Currently this requires explicitly declaration of the events and signal handler to set
    #  the event (gloo_run.py:_launch_jobs()). Need to figure out a generalized way to hide this behind
    #  interfaces.
    stop = threading.Event()
    events = events or []
    for event in events:
        on_event(event, exit_event.set, stop=stop, silent=True)

    try:
        middleman.join()
    except:
        # interrupted, send middleman TERM signal which will terminate children
        exit_event.set()
        while True:
            try:
                middleman.join()
                break
            except:
                # interrupted, wait for middleman to finish
                pass
    finally:
        stop.set()

    stdout_fwd.join()
    stderr_fwd.join()

    return middleman.exitcode