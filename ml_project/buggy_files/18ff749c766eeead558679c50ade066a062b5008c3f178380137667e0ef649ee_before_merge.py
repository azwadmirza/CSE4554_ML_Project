def submit(cluster_config_file, docker, screen, tmux, stop, start,
           cluster_name, port_forward, script, args, script_args):
    """Uploads and runs a script on the specified cluster.

    The script is automatically synced to the following location:

        os.path.join("~", os.path.basename(script))

    Example:
        >>> ray submit [CLUSTER.YAML] experiment.py -- --smoke-test
    """
    assert not (screen and tmux), "Can specify only one of `screen` or `tmux`."
    assert not (script_args and args), "Use -- --arg1 --arg2 for script args."

    if args:
        logger.warning(
            "ray submit [yaml] [script.py] --args=... is deprecated and "
            "will be removed in a future version of Ray. Use "
            "`ray submit [yaml] script.py -- --arg1 --arg2` instead.")

    if start:
        create_or_update_cluster(cluster_config_file, None, None, False, False,
                                 True, cluster_name)

    target = os.path.join("~", os.path.basename(script))
    rsync(cluster_config_file, script, target, cluster_name, down=False)

    command_parts = ["python", target]
    if script_args:
        command_parts += list(script_args)
    elif args is not None:
        command_parts += [args]

    port_forward = [(port, port) for port in list(port_forward)]
    cmd = " ".join(command_parts)
    exec_cluster(
        cluster_config_file,
        cmd,
        docker,
        screen,
        tmux,
        stop,
        start=False,
        override_cluster_name=cluster_name,
        port_forward=port_forward)