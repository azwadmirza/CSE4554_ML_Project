def source_alias(args, stdin=None):
    """Executes the contents of the provided files in the current context.
    If sourced file isn't found in cwd, search for file along $PATH to source
    instead.
    """
    env = builtins.__xonsh_env__
    encoding = env.get('XONSH_ENCODING')
    errors = env.get('XONSH_ENCODING_ERRORS')
    for fname in args:
        if not os.path.isfile(fname):
            fname = locate_binary(fname)
        with open(fname, 'r', encoding=encoding, errors=errors) as fp:
            builtins.execx(fp.read(), 'exec', builtins.__xonsh_ctx__)