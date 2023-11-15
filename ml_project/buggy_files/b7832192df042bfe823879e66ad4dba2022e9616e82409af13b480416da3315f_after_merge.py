def _exec_command(command, use_shell=None, use_tee = None, **env):
    """
    Internal workhorse for exec_command().
    Code from https://github.com/numpy/numpy/pull/7862
    """
    if use_shell is None:
        use_shell = os.name=='posix'
    if use_tee is None:
        use_tee = os.name=='posix'

    executable = None

    if os.name == 'posix' and use_shell:
        # On POSIX, subprocess always uses /bin/sh, override
        sh = os.environ.get('SHELL', '/bin/sh')
        if _is_sequence(command):
            command = [sh, '-c', ' '.join(command)]
        else:
            command = [sh, '-c', command]
        use_shell = False

    elif os.name == 'nt' and _is_sequence(command):
        # On Windows, join the string for CreateProcess() ourselves as
        # subprocess does it a bit differently
        command = ' '.join(_quote_arg(arg) for arg in command)

    # Inherit environment by default
    env = env or None
    try:
        proc = subprocess.Popen(command, shell=use_shell, env=env,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
    except EnvironmentError:
        # Return 127, as os.spawn*() and /bin/sh do
        return '', 127
    text, err = proc.communicate()
    # Only append stderr if the command failed, as otherwise
    # the output may become garbled for parsing
    if proc.returncode:
        if text:
            text += "\n"
        text += err
    # Another historical oddity
    if text[-1:] == '\n':
        text = text[:-1]
    if use_tee:
        print(text)
    return proc.returncode, text