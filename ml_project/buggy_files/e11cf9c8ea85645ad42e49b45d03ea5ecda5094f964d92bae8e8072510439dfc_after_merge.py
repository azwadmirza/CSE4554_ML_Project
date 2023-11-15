def print_exception(msg=None):
    """Print exceptions with/without traceback."""
    env = getattr(builtins, '__xonsh_env__', os.environ)
    if 'XONSH_SHOW_TRACEBACK' not in env:
        sys.stderr.write('xonsh: For full traceback set: '
                         '$XONSH_SHOW_TRACEBACK = True\n')
    if env.get('XONSH_SHOW_TRACEBACK', False):
        traceback.print_exc()
    else:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exception_only = traceback.format_exception_only(exc_type, exc_value)
        sys.stderr.write(''.join(exception_only))
    if msg:
        msg = msg if msg.endswith('\n') else msg + '\n'
        sys.stderr.write(msg)