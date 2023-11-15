def print_exception(msg=None):
    """Print exceptions with/without traceback."""
    env = getattr(builtins, '__xonsh_env__', None)
    # flags indicating whether the traceback options have been manually set
    if env is None:
        env = os.environ
        manually_set_trace = 'XONSH_SHOW_TRACEBACK' in env
        manually_set_logfile ='XONSH_TRACEBACK_LOGFILE' in env
    else:
        manually_set_trace = env.is_manually_set('XONSH_SHOW_TRACEBACK')
        manually_set_logfile = env.is_manually_set('XONSH_TRACEBACK_LOGFILE')
    if (not manually_set_trace) and (not manually_set_logfile):
        # Notify about the traceback output possibility if neither of
        # the two options have been manually set
        sys.stderr.write('xonsh: For full traceback set: '
                         '$XONSH_SHOW_TRACEBACK = True\n')
    # get env option for traceback and convert it if necessary
    show_trace = env.get('XONSH_SHOW_TRACEBACK', False)
    if not is_bool(show_trace):
        show_trace = to_bool(show_trace)
    # if the trace option has been set, print all traceback info to stderr
    if show_trace:
        # notify user about XONSH_TRACEBACK_LOGFILE if it has
        # not been set manually
        if not manually_set_logfile:
            sys.stderr.write('xonsh: To log full traceback to a file set: '
                             '$XONSH_TRACEBACK_LOGFILE = <filename>\n')
        traceback.print_exc()
    # additionally, check if a file for traceback logging has been
    # specified and convert to a proper option if needed
    log_file = env.get('XONSH_TRACEBACK_LOGFILE', None)
    log_file = to_logfile_opt(log_file)
    if log_file:
        # if log_file <> '' or log_file <> None, append
        # traceback log there as well
        with open(os.path.abspath(log_file), 'a') as f:
            traceback.print_exc(file=f)

    if not show_trace:
        # if traceback output is disabled, print the exception's
        # error message on stderr.
        display_error_message()
    if msg:
        msg = msg if msg.endswith('\n') else msg + '\n'
        sys.stderr.write(msg)