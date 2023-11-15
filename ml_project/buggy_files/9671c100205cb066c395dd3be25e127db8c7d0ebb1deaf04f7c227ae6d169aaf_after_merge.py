def _command_is_autocd(cmd):
    if not builtins.__xonsh_env__.get('AUTO_CD', False):
        return False
    try:
        cmd_abspath = os.path.abspath(os.path.expanduser(cmd))
    except (FileNotFoundError, OSError):
        return False
    return os.path.isdir(cmd_abspath)