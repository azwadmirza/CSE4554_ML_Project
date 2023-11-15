def _windows_bash_command(env=None):
    """Determines the command for Bash on windows."""
    wbc = 'bash'
    path = None if env is None else env.get('PATH', None)
    bash_on_path = shutil.which('bash', path=path)
    if bash_on_path:
        # Check if Bash is from the "Windows Subsystem for Linux" (WSL)
        # which can't be used by xonsh foreign-shell/completer
        out = subprocess.check_output([bash_on_path, '--version'],
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
        if 'pc-linux-gnu' in out.splitlines()[0]:
            gfwp = _git_for_windows_path()
            if gfwp:
                bashcmd = os.path.join(gfwp, 'bin\\bash.exe')
                if os.path.isfile(bashcmd):
                    wbc = bashcmd
        else:
            wbc = bash_on_path
    return wbc