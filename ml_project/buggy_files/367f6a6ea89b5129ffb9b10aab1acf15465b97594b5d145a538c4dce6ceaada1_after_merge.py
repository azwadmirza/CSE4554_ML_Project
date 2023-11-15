def _command_is_valid(cmd):
    try:
        cmd_abspath = os.path.abspath(os.path.expanduser(cmd))
    except (FileNotFoundError, OSError):
        return False
    return cmd in builtins.__xonsh_commands_cache__ or \
        (os.path.isfile(cmd_abspath) and os.access(cmd_abspath, os.X_OK))