def bash_completions(prefix, line, begidx, endidx, env=None, paths=None,
                     command=None, quote_paths=_bash_quote_paths, **kwargs):
    """Completes based on results from BASH completion.

    Parameters
    ----------
    prefix : str
        The string to match
    line : str
        The line that prefix appears on.
    begidx : int
        The index in line that prefix starts on.
    endidx : int
        The index in line that prefix ends on.
    env : Mapping, optional
        The environment dict to execute the Bash suprocess in.
    paths : list or tuple of str or None, optional
        This is a list (or tuple) of strings that specifies where the
        ``bash_completion`` script may be found. The first valid path will
        be used. For better performance, bash-completion v2.x is recommended
        since it lazy-loads individual completion scripts. For both
        bash-completion v1.x and v2.x, paths of individual completion scripts
        (like ``.../completes/ssh``) do not need to be included here. The
        default values are platform dependent, but sane.
    command : str or None, optional
        The /path/to/bash to use. If None, it will be selected based on the
        from the environment and platform.
    quote_paths : callable, optional
        A functions that quotes file system paths. You shouldn't normally need
        this as the default is acceptable 99+% of the time.

    Returns
    -------
    rtn : list of str
        Possible completions of prefix, sorted alphabetically.
    lprefix : int
        Length of the prefix to be replaced in the completion.
    """
    source = _get_bash_completions_source(paths) or set()

    if prefix.startswith('$'):  # do not complete env variables
        return set(), 0

    splt = line.split()
    cmd = splt[0]
    idx = n = 0
    prev = ''
    for n, tok in enumerate(splt):
        if tok == prefix:
            idx = line.find(prefix, idx)
            if idx >= begidx:
                break
        prev = tok

    if len(prefix) == 0:
        prefix_quoted = '""'
        n += 1
    else:
        prefix_quoted = shlex.quote(prefix)

    script = BASH_COMPLETE_SCRIPT.format(
        source=source, line=' '.join(shlex.quote(p) for p in splt),
        comp_line=shlex.quote(line), n=n, cmd=shlex.quote(cmd),
        end=endidx + 1, prefix=prefix_quoted, prev=shlex.quote(prev),
    )

    if command is None:
        command = _bash_command(env=env)
    try:
        out = subprocess.check_output(
            [command, '-c', script], universal_newlines=True,
            stderr=subprocess.PIPE, env=env)
    except (subprocess.CalledProcessError, FileNotFoundError,
            UnicodeDecodeError):
        return set(), 0

    out = out.splitlines()
    complete_stmt = out[0]
    out = set(out[1:])

    # From GNU Bash document: The results of the expansion are prefix-matched
    # against the word being completed

    # Ensure input to `commonprefix` is a list (now required by Python 3.6)
    commprefix = os.path.commonprefix(list(out))
    strip_len = 0
    while strip_len < len(prefix):
        if commprefix.startswith(prefix[strip_len:]):
            break
        strip_len += 1

    if '-o noquote' not in complete_stmt:
        out = quote_paths(out, '', '')
    if '-o nospace' in complete_stmt:
        out = set([x.rstrip() for x in out])

    return out, len(prefix) - strip_len