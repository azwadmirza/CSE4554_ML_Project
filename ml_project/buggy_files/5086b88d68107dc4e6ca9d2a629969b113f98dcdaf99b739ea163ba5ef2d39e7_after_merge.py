def fork_shell(env, shellcmd, cwd):
    or_ctrld = '' if windows else "or 'Ctrl+D' "
    err("Launching subshell in virtual environment. Type 'exit' ", or_ctrld,
        "to return.", sep='')
    if 'VIRTUAL_ENV' in os.environ:
        err("Be aware that this environment will be nested on top "
            "of '%s'" % Path(os.environ['VIRTUAL_ENV']).name)
    try:
        inve(env, *shellcmd, cwd=cwd)
    except CalledProcessError:
        # These shells report errors when the last command executed in the
        # subshell in an error. This causes the subprocess to fail, which is
        # not what we want. Stay silent for them, there's nothing we can do.
        shell_name, _ = os.path.splitext(os.path.basename(shellcmd[0]))
        suppress_error = shell_name.tolower() in ['cmd', 'powershell', 'pwsh']
        if not suppress_error:
            raise