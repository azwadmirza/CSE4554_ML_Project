def _writer_daemon(stdin, read_fd, write_fd, echo, log_file, control_pipe):
    """Daemon used by ``log_output`` to write to a log file and to ``stdout``.

    The daemon receives output from the parent process and writes it both
    to a log and, optionally, to ``stdout``.  The relationship looks like
    this::

        Terminal
           |
           |          +-------------------------+
           |          | Parent Process          |
           +--------> |   with log_output():    |
           | stdin    |     ...                 |
           |          +-------------------------+
           |            ^             | write_fd (parent's redirected stdout)
           |            | control     |
           |            | pipe        |
           |            |             v read_fd
           |          +-------------------------+   stdout
           |          | Writer daemon           |------------>
           +--------> |   read from read_fd     |   log_file
             stdin    |   write to out and log  |------------>
                      +-------------------------+

    Within the ``log_output`` handler, the parent's output is redirected
    to a pipe from which the daemon reads.  The daemon writes each line
    from the pipe to a log file and (optionally) to ``stdout``.  The user
    can hit ``v`` to toggle output on ``stdout``.

    In addition to the input and output file descriptors, the daemon
    interacts with the parent via ``control_pipe``.  It reports whether
    ``stdout`` was enabled or disabled when it finished and, if the
    ``log_file`` is a ``StringIO`` object, then the daemon also sends the
    logged output back to the parent as a string, to be written to the
    ``StringIO`` in the parent. This is mainly for testing.

    Arguments:
        stdin (stream): input from the terminal
        read_fd (int): pipe for reading from parent's redirected stdout
        write_fd (int): parent's end of the pipe will write to (will be
            immediately closed by the writer daemon)
        echo (bool): initial echo setting -- controlled by user and
            preserved across multiple writer daemons
        log_file (file-like): file to log all output
        control_pipe (Pipe): multiprocessing pipe on which to send control
            information to the parent

    """
    # Use line buffering (3rd param = 1) since Python 3 has a bug
    # that prevents unbuffered text I/O.
    in_pipe = os.fdopen(read_fd, 'r', 1)
    os.close(write_fd)

    # list of streams to select from
    istreams = [in_pipe, stdin] if stdin else [in_pipe]
    force_echo = False      # parent can force echo for certain output

    try:
        with keyboard_input(stdin) as kb:
            while True:
                # fix the terminal settings if we recently came to
                # the foreground
                kb.check_fg_bg()

                # wait for input from any stream. use a coarse timeout to
                # allow other checks while we wait for input
                rlist, _, _ = _retry(select.select)(istreams, [], [], 1e-1)

                # Allow user to toggle echo with 'v' key.
                # Currently ignores other chars.
                # only read stdin if we're in the foreground
                if stdin in rlist and not _is_background_tty(stdin):
                    # it's possible to be backgrounded between the above
                    # check and the read, so we ignore SIGTTIN here.
                    with ignore_signal(signal.SIGTTIN):
                        try:
                            if stdin.read(1) == 'v':
                                echo = not echo
                        except IOError as e:
                            # If SIGTTIN is ignored, the system gives EIO
                            # to let the caller know the read failed b/c it
                            # was in the bg. Ignore that too.
                            if e.errno != errno.EIO:
                                raise

                if in_pipe in rlist:
                    # Handle output from the calling process.
                    line = _retry(in_pipe.readline)()
                    if not line:
                        break

                    # find control characters and strip them.
                    controls = control.findall(line)
                    line = control.sub('', line)

                    # Echo to stdout if requested or forced.
                    if echo or force_echo:
                        sys.stdout.write(line)
                        sys.stdout.flush()

                    # Stripped output to log file.
                    log_file.write(_strip(line))
                    log_file.flush()

                    if xon in controls:
                        force_echo = True
                    if xoff in controls:
                        force_echo = False

    except BaseException:
        tty.error("Exception occurred in writer daemon!")
        traceback.print_exc()

    finally:
        # send written data back to parent if we used a StringIO
        if isinstance(log_file, StringIO):
            control_pipe.send(log_file.getvalue())
        log_file.close()

    # send echo value back to the parent so it can be preserved.
    control_pipe.send(echo)