def rsync(config_file: str,
          source: Optional[str],
          target: Optional[str],
          override_cluster_name: Optional[str],
          down: bool,
          ip_address: Optional[str] = None,
          use_internal_ip: bool = False,
          no_config_cache: bool = False,
          all_nodes: bool = False,
          _runner: ModuleType = subprocess) -> None:
    """Rsyncs files.

    Arguments:
        config_file: path to the cluster yaml
        source: source dir
        target: target dir
        override_cluster_name: set the name of the cluster
        down: whether we're syncing remote -> local
        ip_address (str): Address of node. Raise Exception
            if both ip_address and 'all_nodes' are provided.
        use_internal_ip (bool): Whether the provided ip_address is
            public or private.
        all_nodes: whether to sync worker nodes in addition to the head node
    """
    if bool(source) != bool(target):
        cli_logger.abort(
            "Expected either both a source and a target, or neither.")

    assert bool(source) == bool(target), (
        "Must either provide both or neither source and target.")

    if ip_address and all_nodes:
        cli_logger.abort("Cannot provide both ip_address and 'all_nodes'.")

    config = yaml.safe_load(open(config_file).read())
    if override_cluster_name is not None:
        config["cluster_name"] = override_cluster_name
    config = _bootstrap_config(config, no_config_cache=no_config_cache)

    is_file_mount = False
    if source and target:
        for remote_mount in config.get("file_mounts", {}).keys():
            if (source if down else target).startswith(remote_mount):
                is_file_mount = True
                break

    provider = _get_node_provider(config["provider"], config["cluster_name"])

    def rsync_to_node(node_id, is_head_node):
        updater = NodeUpdaterThread(
            node_id=node_id,
            provider_config=config["provider"],
            provider=provider,
            auth_config=config["auth"],
            cluster_name=config["cluster_name"],
            file_mounts=config["file_mounts"],
            initialization_commands=[],
            setup_commands=[],
            ray_start_commands=[],
            runtime_hash="",
            use_internal_ip=use_internal_ip,
            process_runner=_runner,
            file_mounts_contents_hash="",
            is_head_node=is_head_node,
            rsync_options={
                "rsync_exclude": config.get("rsync_exclude"),
                "rsync_filter": config.get("rsync_filter")
            },
            docker_config=config.get("docker"))
        if down:
            rsync = updater.rsync_down
        else:
            rsync = updater.rsync_up

        if source and target:
            # print rsync progress for single file rsync
            if cli_logger.verbosity > 0:
                cmd_output_util.set_output_redirected(False)
                set_rsync_silent(False)
            rsync(source, target, is_file_mount)
        else:
            updater.sync_file_mounts(rsync)

    nodes = []
    head_node = _get_head_node(
        config, config_file, override_cluster_name, create_if_needed=False)
    if ip_address:
        nodes = [
            provider.get_node_id(ip_address, use_internal_ip=use_internal_ip)
        ]
    else:
        nodes = [head_node]
        if all_nodes:
            nodes.extend(_get_worker_nodes(config, override_cluster_name))

    for node_id in nodes:
        rsync_to_node(node_id, is_head_node=(node_id == head_node))