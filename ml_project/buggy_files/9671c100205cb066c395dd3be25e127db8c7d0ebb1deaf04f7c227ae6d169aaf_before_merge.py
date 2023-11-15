def _command_is_autocd(cmd):
    if not builtins.__xonsh_env__.get('AUTO_CD', False):
        return False
    cmd_abspath = os.path.abspath(os.path.expanduser(cmd))
    return os.path.isdir(cmd_abspath)