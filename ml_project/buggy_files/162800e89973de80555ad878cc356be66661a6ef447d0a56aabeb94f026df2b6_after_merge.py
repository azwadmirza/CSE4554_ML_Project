def submit(cluster_config_file, screen, tmux, stop, start, cluster_name,
           port_forward, script, args, script_args, log_new_style, log_color,
           verbose):
    """Uploads and runs a script on the specified cluster.

    The script is automatically synced to the following location:

        os.path.join("~", os.path.basename(script))

    Example:
        >>> ray submit [CLUSTER.YAML] experiment.py -- --smoke-test
    """
    cli_logger.old_style = not log_new_style
    cli_logger.color_mode = log_color
    cli_logger.verbosity = verbose

    set_output_redirected(False)

    cli_logger.doassert(not (screen and tmux),
                        "`{}` and `{}` are incompatible.", cf.bold("--screen"),
                        cf.bold("--tmux"))
    cli_logger.doassert(
        not (script_args and args),
        "`{0}` and `{1}` are incompatible. Use only `{1}`.\n"
        "Example: `{2}`", cf.bold("--args"), cf.bold("-- <args ...>"),
        cf.bold("ray submit script.py -- --arg=123 --flag"))

    assert not (screen and tmux), "Can specify only one of `screen` or `tmux`."
    assert not (script_args and args), "Use -- --arg1 --arg2 for script args."

    if args:
        cli_logger.warning(
            "`{}` is deprecated and will be removed in the future.",
            cf.bold("--args"))
        cli_logger.warning("Use `{}` instead. Example: `{}`.",
                           cf.bold("-- <args ...>"),
                           cf.bold("ray submit script.py -- --arg=123 --flag"))
        cli_logger.newline()
        cli_logger.old_warning(
            logger,
            "ray submit [yaml] [script.py] --args=... is deprecated and "
            "will be removed in a future version of Ray. Use "
            "`ray submit [yaml] script.py -- --arg1 --arg2` instead.")

    if start:
        create_or_update_cluster(
            config_file=cluster_config_file,
            override_min_workers=None,
            override_max_workers=None,
            no_restart=False,
            restart_only=False,
            yes=True,
            override_cluster_name=cluster_name,
            no_config_cache=False,
            dump_command_output=True,
            use_login_shells=True)
    target = os.path.basename(script)
    target = os.path.join("~", target)
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
        cmd=cmd,
        run_env="docker",
        screen=screen,
        tmux=tmux,
        stop=stop,
        start=False,
        override_cluster_name=cluster_name,
        port_forward=port_forward)