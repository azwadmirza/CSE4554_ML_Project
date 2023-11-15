def _windows_bash_command(env=None):
    """Determines the command for Bash on windows."""
    wbc = 'bash'
    path = None if env is None else env.get('PATH', None)
    bash_on_path = shutil.which('bash', path=path)
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
            bash_works = out and 'pc-linux-gnu' not in out.splitlines()[0]

        if bash_works:
            wbc = bash_on_path
        else:
            gfwp = _git_for_windows_path()
            if gfwp:
                bashcmd = os.path.join(gfwp, 'bin\\bash.exe')
                if os.path.isfile(bashcmd):
                    wbc = bashcmd
    return wbc