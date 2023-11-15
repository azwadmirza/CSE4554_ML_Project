def exec_cluster(config_file,
                 cmd=None,
                 docker=False,
                 screen=False,
                 tmux=False,
                 stop=False,
                 start=False,
                 override_cluster_name=None,
                 port_forward=None,
                 with_output=False):
    """Runs a command on the specified cluster.

    Arguments:
        config_file: path to the cluster yaml
        cmd: command to run
        docker: whether to run command in docker container of config
        screen: whether to run in a screen
        tmux: whether to run in a tmux session
        stop: whether to stop the cluster after command run
        start: whether to start the cluster if it isn't up
        override_cluster_name: set the name of the cluster
        port_forward (int or list[int]): port(s) to forward
    """
    assert not (screen and tmux), "Can specify only one of `screen` or `tmux`."

    config = yaml.safe_load(open(config_file).read())
    if override_cluster_name is not None:
        config["cluster_name"] = override_cluster_name
    config = _bootstrap_config(config)

    head_node = _get_head_node(
        config, config_file, override_cluster_name, create_if_needed=start)

    provider = get_node_provider(config["provider"], config["cluster_name"])
    try:
        updater = NodeUpdaterThread(
            node_id=head_node,
            provider_config=config["provider"],
            provider=provider,
            auth_config=config["auth"],
            cluster_name=config["cluster_name"],
            file_mounts=config["file_mounts"],
            initialization_commands=[],
            setup_commands=[],
            ray_start_commands=[],
            runtime_hash="",
        )

        def wrap_docker(command):
            container_name = config["docker"]["container_name"]
            if not container_name:
                raise ValueError("Docker container not specified in config.")
            return with_docker_exec(
                [command], container_name=container_name)[0]

        if cmd:
            cmd = wrap_docker(cmd) if docker else cmd

            if stop:
                shutdown_cmd = (
                    "ray stop; ray teardown ~/ray_bootstrap_config.yaml "
                    "--yes --workers-only")
                if docker:
                    shutdown_cmd = wrap_docker(shutdown_cmd)
                cmd += ("; {}; sudo shutdown -h now".format(shutdown_cmd))

        result = _exec(
            updater,
            cmd,
            screen,
            tmux,
            port_forward=port_forward,
            with_output=with_output)

        if tmux or screen:
            attach_command_parts = ["ray attach", config_file]
            if override_cluster_name is not None:
                attach_command_parts.append(
                    "--cluster-name={}".format(override_cluster_name))
            if tmux:
                attach_command_parts.append("--tmux")
            elif screen:
                attach_command_parts.append("--screen")

            attach_command = " ".join(attach_command_parts)
            attach_info = "Use `{}` to check on command status.".format(
                attach_command)
            logger.info(attach_info)
        return result
    finally:
        provider.cleanup()