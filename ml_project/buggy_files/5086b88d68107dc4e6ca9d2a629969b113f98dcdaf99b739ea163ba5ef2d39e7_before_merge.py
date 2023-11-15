def fork_shell(env, shellcmd, cwd):
    or_ctrld = '' if windows else "or 'Ctrl+D' "
    err("Launching subshell in virtual environment. Type 'exit' ", or_ctrld,
        "to return.", sep='')
    if 'VIRTUAL_ENV' in os.environ:
        err("Be aware that this environment will be nested on top "
            "of '%s'" % Path(os.environ['VIRTUAL_ENV']).name)
    inve(env, *shellcmd, cwd=cwd)