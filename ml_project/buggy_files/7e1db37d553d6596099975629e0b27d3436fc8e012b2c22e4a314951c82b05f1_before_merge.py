def windows_bash_command():
    """Determines the command for Bash on windows."""
    # Check that bash is on path otherwise try the default directory
    # used by Git for windows
    wbc = 'bash'
    cmd_cache = builtins.__xonsh_commands_cache__
    bash_on_path = cmd_cache.lazy_locate_binary('bash', ignore_alias=True)
    if bash_on_path:
        try:
            out = subprocess.check_output([bash_on_path, '--version'],
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)
        except subprocess.CalledProcessError:
            bash_works = False
        else:
            # Check if Bash is from the "Windows Subsystem for Linux" (WSL)
            # which can't be used by xonsh foreign-shell/completer
            bash_works = 'pc-linux-gnu' not in out.splitlines()[0]

        if bash_works:
            wbc = bash_on_path
        else:
            gfwp = git_for_windows_path()
            if gfwp:
                bashcmd = os.path.join(gfwp, 'bin\\bash.exe')
                if os.path.isfile(bashcmd):
                    wbc = bashcmd
    return wbc