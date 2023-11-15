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
            cmd_output_util.set_output_redirected(False)
            set_rsync_silent(False)
            rsync(source, target, is_file_mount)
        else:
            updater.sync_file_mounts(rsync)