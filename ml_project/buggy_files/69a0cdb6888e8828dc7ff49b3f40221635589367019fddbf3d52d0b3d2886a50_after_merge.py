def check_write(command, prefix, json=False):
    if inroot_notwritable(prefix):
        from .help import root_read_only
        root_read_only(command, prefix, json=json)