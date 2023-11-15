def CCompiler_spawn(self, cmd, display=None):
    """
    Execute a command in a sub-process.

    Parameters
    ----------
    cmd : str
        The command to execute.
    display : str or sequence of str, optional
        The text to add to the log file kept by `numpy.distutils`.
        If not given, `display` is equal to `cmd`.

    Returns
    -------
    None

    Raises
    ------
    DistutilsExecError
        If the command failed, i.e. the exit status was not 0.

    """
    if display is None:
        display = cmd
        if is_sequence(display):
            display = ' '.join(list(display))
    log.info(display)
    s,o = exec_command(cmd)
    if s:
        if is_sequence(cmd):
            cmd = ' '.join(list(cmd))
        print(o)
        if re.search('Too many open files', o):
            msg = '\nTry rerunning setup command until build succeeds.'
        else:
            msg = ''
        raise DistutilsExecError('Command "%s" failed with exit status %d%s' % (cmd, s, msg))